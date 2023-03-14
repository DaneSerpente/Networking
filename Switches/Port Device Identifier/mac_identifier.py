import csv, requests, time

# Convert the Mac address table file to CSV
with open('mac_address_table.txt', 'r') as infile:
    # create the CSV file and open it for writing
    with open('mac_address_table.csv', 'w', newline='') as outfile:
        # create a CSV writer object
        writer = csv.writer(outfile)
        # loop through the lines in the text file
        for line in infile:
            # split the line into columns
            columns = line.strip().split()
            # write the columns to the CSV file
            writer.writerow(columns)
            
# Read the MAC address table file
with open('mac_address_table.csv', 'r') as f:
    mac_table = f.readlines()

# Read the MAC OUI file
with open('mac_oui.txt', 'r') as f:
    mac_oui = f.readlines()
    
# Read the Interface Status file
with open('int_status.txt', 'r') as f:
    int_status = f.readlines() 
    
# Read the ARP file
with open('arp.txt', 'r') as f:
    arp_table = f.readlines() 
    
def oui_lookup(mac_address):
    # Use the macvendors API to grab the vendor based on OUI
    vendor = requests.get("https://api.macvendors.com/" + mac_address)
    time.sleep(1/10)
    return vendor.text

# Create a dictionary of MAC Addresses and vendor descriptions
vendor_dict = {}
for line in mac_table:
    fields = line.split(',')
    mac = fields[1]
    vendor = oui_lookup(mac)
    vendor_dict[mac] = ''.join(vendor)

# Create a dictionary of Mac addresses and IP addresses
arp_dict = {}
for line in arp_table:
    fields = line.split()
    if fields[3] != "Incomplete":
        arp_dict[fields[3]] = ''.join(fields[1]) 
     
# Create a dictionary of interfaces and descriptions
int_dict = {}
for line in int_status:
    fields = line.strip().split('  ')
    int_dict[fields[0]] = ''.join(fields[1])   

# Clean up Interfaces and Descriptions
unwanted_words = ['connected', 'notconnect']
for key, value in int_dict.items():
    for word in unwanted_words:
        if word in value:
            int_dict[key] = value.replace(word, '').strip()

# Process each line in the MAC address table
new_mac_table = []
for line in mac_table:
    fields = [field.strip() for field in line.split(',')]
    # Delete unwated fields
    del fields[2]
    mac = fields[1]
    port = fields[2]
    # Add the IPs
    if mac in arp_dict:
        fields.append(arp_dict[mac])
    if mac not in arp_dict:
        fields.append('')
    # Add the interface description
    if port in int_dict:
        fields.append(int_dict[port])
    # Add the vendor based on OUI
    if mac in vendor_dict:
        fields.append(vendor_dict[mac])
    new_mac_table.append('\t'.join(fields))

# Write the results to CSV
with open('device_details.csv', 'w', newline='') as csvfile:
    # Create a CSV writer object
    writer = csv.writer(csvfile)

    # Write the header row
    writer.writerow(['VLAN', 'MAC Address', 'Interface', 'IP Address', 'Port Description', 'OUI Vendor'])

    # Write the data rows
    for row in new_mac_table:
        columns = row.strip().split('\t')
        writer.writerow(columns)