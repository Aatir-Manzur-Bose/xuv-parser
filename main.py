# This is a sample Python script.

# look out for where the partition starts from, partitions are shown from lines 36-45
# offset is length of preceding partitions combined

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

flash_schema = {
    "flash_device": {
        "block_size": 4 * 1024,
        # Boot block is common for both banks, but only bank A is used.
        # To ensure DFU works with ADK20.1 and earlier projects, boot_block_size must be set to 16 * 4 *1024.
        # boot_block_size is set to 1 * 4 *1024, for more efficient flash usage
        "boot_block_size": 1 * 4 * 1024,
        "alt_image_offset": 2048 * 4 * 1024
    },
    "encrypt": False,
    "layout": [
        # image_header partition
        ("curator_fs", {"capacity": 3 * 4096, "authenticate": False, "src_file_signed": False}),
        ("apps_p0", {"capacity": 162 * 4096, "authenticate": True, "src_file_signed": True}),
        ("apps_p1", {"capacity": 554 * 4096, "authenticate": False}),
        # Device config filesystem size limited by size of production test buffer,  ( 1024*2)-10.
        # WARNING: this partition cannot be resized via a DFU update.  See
        # https://qualcomm-cdmatech-support.my.salesforce.com/5004V00001DW7sf
        # for details.
        ("device_ro_fs", {"capacity": 16 * 4096, "authenticate": False, "inline_auth_hash": True}),
        ("rw_config", {"capacity": 32 * 4096}),
        ("rw_fs", {"capacity": 1 * 4096}),
        ("debug_partition", {"capacity": 99 * 4096}),
        ("ra_partition", {"capacity": 69 * 4096, "id": ""}),
        ("ro_cfg_fs", {"capacity": 53 * 4096, "authenticate": False}),
        ("ro_fs", {"capacity": 1057 * 4096, "authenticate": False})
    ]
}

# divide by 4 to represent sectors within partitions
curator_fs_array = bytearray([0xde, 0xad, 0xbe, 0xef] * ((3 * 4096) // 4))
apps_p0_array = bytearray([0xde, 0xad, 0xbe, 0xef] * ((162 * 4096) // 4))
apps_p1_array = bytearray([0xde, 0xad, 0xbe, 0xef] * ((554 * 4096) // 4))
device_ro_fs_array = bytearray([0xde, 0xad, 0xbe, 0xef] * ((16 * 4096) // 4))
rw_config_array = bytearray([0xde, 0xad, 0xbe, 0xef] * ((32 * 4096) // 4))
rw_fs_array = bytearray([0xde, 0xad, 0xbe, 0xef] * ((1 * 4096) // 4))
debug_partition_array = bytearray([0xde, 0xad, 0xbe, 0xef] * ((99 * 4096) // 4))
ra_partition_array = bytearray([0xde, 0xad, 0xbe, 0xef] * ((69 * 4096) // 4))
ro_cfg_fs_array = bytearray([0xde, 0xad, 0xbe, 0xef] * ((53 * 4096) // 4))
ro_fs_array = bytearray([0xde, 0xad, 0xbe, 0xef] * ((1057 * 4096) // 4))

sections = {"curator_fs": {}, "apps_p0": {}, "apps_p1": {}, "device_ro_fs": {},
            "rw_config": {}, "rw_fs": {}, "debug_partition": {}, "ra_partition": {}
            , "ro_cfg_fs": {}, "ro_fs": {}}
names = ["curator_fs", "apps_p0", "apps_p1", "device_ro_fs", "rw_config", "rw_fs", "debug_partition", "ra_partition",
         "ro_cfg_fs", "ro_fs"]
capacities = [(3 * 4096)//4, (162 * 4096)//4, (554 * 4096)//4, (16 * 4096)//4, (32 * 4096)//4, (1 * 4096)//4, (99 * 4096)//4, (69 * 4096)//4,
              (53 * 4096)//4, (1057 * 4096)//4]

partition_capacities = [[curator_fs_array, 0, 0], [apps_p0_array, 0, 0], [apps_p1_array, 0, 0], [device_ro_fs_array, 0, 0],
                        [rw_config_array, 0, 0], [rw_fs_array, 0, 0], [debug_partition_array, 0, 0],
                        [ra_partition_array, 0, 0], [ro_cfg_fs_array, 0, 0], [ro_fs_array, 0, 0]]

file_ranges_max = [None] * 10
file_ranges_max[0] = (3 * 4096) // 4
for x in range(1, len(capacities)):
    file_ranges_max[x] = capacities[x] + file_ranges_max[x - 1]

file_ranges_min = [None] * 10
file_ranges_min[0] = 0
for y in range(1, len(file_ranges_max)):
    file_ranges_min[y] = file_ranges_max[y-1]

for j in range(len(partition_capacities)):
    partition_capacities[j][2] = file_ranges_max[j]
for k in range(len(partition_capacities)):
    partition_capacities[j][1] = file_ranges_min[j]


# modify i (offset) as well as while loop variables
def read_section_from_xuv():
    f = open("flash_image.xuv", "r")
    g = open("flash_image_formatted.xuv", "w")

    for line in f:
        if line.strip():
            g.write("\t".join(line.split()[1:]) + "\n")

    f.close()
    g.close()
    with open('flash_image_formatted.xuv', 'rb') as f:
        hexdata = f.read().hex()

    # i = 0
    # while i < capacity:
    #     partition[i] = int(hexdata[i], 16)
    #     i += 1

    i = 0
    for j in range(len(partition_capacities)):
        k = 0
        while partition_capacities[j][1] <= i < partition_capacities[j][2]:
            partition_capacities[j][0][k] = int(hexdata[i], 16)
            i += 1
            k += 1



# modify i (offset) and while loop variables... j = 3 * 4096 ... while j < 162 * 4096 (second partition size)
# run find length for each section array
def find_length() -> int:
    for z in range(len(capacities)):
        i = 0
        while i < capacities[z]:
            if hex(partition_capacities[z][0][i]) == '0xd':
                print("here")
                sections.get(names[z])["size"] = i
                break
            i += 1


def print_flash_usage_table():
    """Prints a table with flash usage information for each section in the image

    """

    block_size = 4 * 1024

    column_width = 14

    header_row = "{:^{w}s} |" * 5
    unit_blocks = "Blocks"
    unit_bytes = "Bytes"
    table_header = [
        header_row.format("Name", "Capacity", "Used", "Unused", "Image size", w=column_width),
        header_row.format("", unit_blocks, unit_blocks, unit_blocks, unit_bytes, w=column_width)
    ]

    data_row = "{:<{w}s} |" + "{:^{w}s} |" * 4
    totals = {
        "capacity": 0,
        "used": 0,
        "unused": 0,
        "size": 0
    }
    table_data = []
    capacity_blocks = (3 * 4096) // block_size
    capacity = "{:2d}".format(capacity_blocks)

    # dictionary within a dictionary
    for section in sections:
        name = section
        print(name)
        # This line starts another nested loop. It iterates over the key-value pairs within the dictionary associated
        # with the current. j is the key and k is the value (size (j) = k)
        for j, k in sections[section].items():
            used_blocks = k // block_size + (k % block_size > 0)
            used = "{:2d}".format(used_blocks)

            unused_blocks = capacity_blocks - used_blocks
            unused = "{:2d}".format(unused_blocks)

            size = "{:9d}".format(k)

            table_data.append(data_row.format(name, capacity, used, unused, size, w=column_width))

            totals['capacity'] = int(totals['capacity']) + capacity_blocks
            totals['used'] = int(totals['used']) + used_blocks
            totals['unused'] = int(unused_blocks)
            totals['size'] = int(k)

            totals['capacity'] = "{:2d}".format(totals['capacity'])
            totals['used'] = "{:2d}".format(totals['used'])
            totals['unused'] = "{:2d}".format(totals['unused'])
            totals['size'] = "{:9d}".format(totals['size'])

            table_data.append(data_row.format("Totals:",
                                              totals['capacity'], totals['used'], totals['unused'], totals['size'],
                                              w=column_width))

    print("Block size: {:d} Bytes\n".format(block_size))
    print("\n".join(table_header + table_data) + "\n")


def print_stats():
    # Use a breakpoint in the code line below to debug your script.
    print(''.join(format(x, '02x') for x in curator_fs_array))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    read_section_from_xuv()
    find_length()
    print_flash_usage_table()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
