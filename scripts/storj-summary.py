#!/usr/bin/env python3

import math, json, re, sys, os
import getopt as go
from storjutils import StorjNode
from beautifultable import BeautifulTable
from colorama import Fore, Back, Style
from pyfiglet import figlet_format
from datetime import date

# GLOBALS
####################
HEADER_TEXT_COLOR = 'cyan'
ENABLE_COLOR = False
TABLE_WIDTH = 410
TABLE_STYLE = BeautifulTable.STYLE_DEFAULT
COLOR_PAIRS = {}    # Initialized in main()

# Functions
###################
def print_usage():
    print()
    print(f'Usage: {sys.argv[0]} [--no-color] [--style=STYLE] [--width=WIDTH][-h, --help]')
    print()
    print('Optional Arguments:')
    print(' -h, --help              Show this help message and quit.')
    print(' --color                 Add color coding to the output.')
    print(' --style=STYLE           Changes the style of the table. Valid arguments are')
    print('                         none, rounded, grid and doubled')
    print(" --width=WIDTH           Sets the table's max width. Integers only, floats will.")
    print('                         be truncated.')
    print()

def parseopt():
    global ENABLE_COLOR, HEADER_TEXT_COLOR, TABLE_STYLE, TABLE_WIDTH

    options = go.getopt(sys.argv[1:], 'h', ['color', 'help', 'style=', 'width='])[0]

    for opt, arg in options:
        if opt in ('-h', '--help'):
            print_usage()
            sys.exit(1)
        elif '--color' == opt:
            ENABLE_COLOR = True
        elif '--style' == opt:
            styles =    {
                            'none': BeautifulTable.STYLE_NONE,
                            'rounded': BeautifulTable.STYLE_BOX_ROUNDED,
                            'grid': BeautifulTable.STYLE_GRID,
                            'doubled': BeautifulTable.STYLE_BOX_DOUBLED
                        }
            TABLE_STYLE = styles[arg]
        elif '--width' == opt:
            TABLE_WIDTH = int(arg)

def colored(word, color, ground=Fore):
    '''
    Valid ground arguments: Fore, Back
    '''
    colors =    {
                    "green": ground.GREEN,
                    "red": ground.RED,
                    "blue": ground.BLUE,
                    "yellow": ground.YELLOW,
                    "magenta": ground.MAGENTA,
                    "cyan": ground.CYAN,
                    "black": ground.BLACK,
                    "white": ground.WHITE
                }

    if color not in colors.keys():
        raise ValueError('colored(): {} is not a valid color.'.format(color))
    elif not ENABLE_COLOR:
        return word
    else:
        return colors[color.lower()] + word + Style.RESET_ALL

def format_bytes(size, power=1024):
    n = 0
    power_labels = {0: '', 1:'k', 2: 'M', 3: 'G', 4: 'T', 5: 'P'}
    while size > power:
        size /= power
        n += 1
    return size, power_labels[n] + 'B'

def text_to_bytes(text):
    '''
    Converts size from readable text format to bytes

    Example: text = 3.39GB
    returns 3390000000
    '''
    readable_size_regex = re.compile(r'(\d+.\d+)\s?([kMGTP]?B)')
    mo = readable_size_regex.search(text)

    if None == mo:
        raise ValueError('text_to_bytes(): Regex could not match text')
    else:
        multiplier = {'B': 1, 'k': 10**3, 'M': 10**6, 'G': 10**9, 'T': 10**12, 'P': 10**15}
        return mo.group(1) * multiplier(mo.group(2)[0])

def format_duration(delta):
    return '{}d {:0.0f}h'.format(delta.days, math.floor(delta.seconds/3600))

def strip_ansi(text):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def general_info_table(stats):
    alignment = BeautifulTable.ALIGN_LEFT
    style = BeautifulTable.STYLE_DOTTED
    tables = []

    # Create General Statistics Table
    ###############################################################################################################
    gen_table = BeautifulTable()
    gen_table.set_style(style)
    gen_table.border.left = ''
    gen_table.border.right = ''
    gen_table.border.top = ''
    gen_table.border.bottom = ''
    gen_table.rows.append(['Current Period', date.today().strftime('%B %Y')])
    #gen_table.rows.append(['Earnings', 'placeholder'])
    #gen_table.rows.append(['Minimum Version Allowed', 'placeholder'])
    gen_table.columns.alignment = alignment
    tables.append(gen_table)

    # Create Node Statistics Table
    ###############################################################################################################
    nodestats_table = BeautifulTable()
    nodestats_table.set_style(style)
    nodestats_table.border.left = ''
    nodestats_table.border.right = ''
    nodestats_table.border.top = ''
    nodestats_table.border.bottom = ''
    nodestats_table.rows.append(['Total', stats['Total Nodes']])
    nodestats_table.rows.append(['Online', stats['Total Nodes Online']])
    nodestats_table.rows.append(['Up-To-Date', stats['Total Nodes UpToDate']])
    nodestats_table.columns.alignment = alignment
    tables.append(nodestats_table)

    # Create Disk Statistics Table
    ###############################################################################################################

    disk_table = BeautifulTable()
    disk_table.set_style(style)
    disk_table.border.left = ''
    disk_table.border.right = ''
    disk_table.border.top = ''
    disk_table.border.bottom = ''
    disk_table.rows.append(['Allocated', '{:.2f} {}'.format(*format_bytes(stats['Total Disk Allocated'], 1000))])
    disk_table.rows.append(['Used', '{:.2f} {}'.format(*format_bytes(stats['Total Disk Used'], 1000))])
    disk_table.rows.append(['Free', '{:.2f} {}'.format(*format_bytes(stats['Total Disk Allocated'] - stats['Total Disk Used'], 1000))])
    disk_table.columns.alignment = alignment
    tables.append(disk_table)

    # Create Bandwidth Statistics Table
    ###############################################################################################################
    bandwidth_table = BeautifulTable()
    bandwidth_table.set_style(style)
    bandwidth_table.border.left = ''
    bandwidth_table.border.right = ''
    bandwidth_table.border.top = ''
    bandwidth_table.border.bottom = ''
    bandwidth_table.rows.append(['Egress', '{:.2f} {}'.format(*format_bytes(stats['Total Bandwidth Egress'], 1000))])
    bandwidth_table.rows.append(['Ingress', '{:.2f} {}'.format(*format_bytes(stats['Total Bandwidth Ingress'], 1000))])
    bandwidth_table.rows.append(['Utilization', '{:.2f} {}'.format(*format_bytes(stats['Total Bandwidth Utilization'], 1000))])
    bandwidth_table.columns.alignment = alignment
    tables.append(bandwidth_table)

    # Create Legend Table
    ###############################################################################################################
    legend_table = BeautifulTable()
    legend_table.set_style(style)
    legend_table.border.left = ''
    legend_table.border.right = ''
    legend_table.border.top = ''
    legend_table.border.bottom = ''
    legend_table.rows.append(['C/S/D', 'Connected/Suspended/Disqualified'])
    legend_table.rows.append(['N/A', 'Not Available'])
    legend_table.columns.alignment = alignment
    tables.append(legend_table)

    return tables

def summary_table(storj_nodes):
    table = BeautifulTable(maxwidth = TABLE_WIDTH)
    table.set_style(TABLE_STYLE)
    table.border.left = ''
    table.border.right = ''
    table.border.top = ''
    table.border.bottom = ''
    header =    [
                    colored('NAME', HEADER_TEXT_COLOR),
                    colored('ID', HEADER_TEXT_COLOR),
                    colored('Status', HEADER_TEXT_COLOR),
                    colored('Uptime', HEADER_TEXT_COLOR),
                    colored('Age', HEADER_TEXT_COLOR),
                    colored('Version', HEADER_TEXT_COLOR),
                    colored('Up To Date', HEADER_TEXT_COLOR),
                    colored('Disk Allocated / % Used', HEADER_TEXT_COLOR),
                    colored('Bandwidth Utilization\n(Ingress + Egress)', HEADER_TEXT_COLOR),
                    colored('Satellites\nC/S/D', HEADER_TEXT_COLOR),
                    colored('Vetting Progress', HEADER_TEXT_COLOR)
                ]

    # Gather overall statistics for general info table while creating the summary
    # Saves time by avoiding parsing the summary table again to get stats.
    statistics =    {
                        'Total Nodes': 0,
                        'Total Nodes Online': 0,
                        'Total Nodes UpToDate': 0,
                        'Total Disk Allocated': 0,
                        'Total Disk Used': 0,
                        'Total Bandwidth Utilization': 0,
                        'Total Bandwidth Egress': 0,
                        'Total Bandwidth Ingress': 0
                    }

    for n in storj_nodes:
        statistics['Total Nodes'] += 1
        if n.is_available():
            disk_allocated = n.get_disk_allocated()
            disk_used = n.get_disk_used()
            bw_egress, bw_ingress, bw_utilization = n.get_bandwidth()
            is_updated = n.is_updated()

            statistics['Total Disk Allocated'] += disk_allocated
            statistics['Total Disk Used'] += disk_used
            statistics['Total Bandwidth Utilization'] += bw_utilization
            statistics['Total Bandwidth Egress'] += bw_egress
            statistics['Total Bandwidth Ingress'] += bw_ingress
            statistics['Total Nodes Online'] += 1
            if is_updated:
                statistics['Total Nodes UpToDate'] += 1


            disk_usage_percent = (disk_used / disk_allocated) * 100
            disk_allocated = '{:.2f}{}'.format(*format_bytes(disk_allocated, 1000))

            table.rows.append([
                n.name,
                n.get_id(),
                COLOR_PAIRS['online'],
                format_duration(n.get_uptime()),
                format_duration(n.get_age()),
                n.get_version(),
                COLOR_PAIRS['yes' if is_updated else 'no'],
                f'{disk_allocated} / {disk_usage_percent:.2f}%',
                '{:.2f}{}'.format(*format_bytes(bw_utilization, 1000)),
                '{}/{}/{}'.format(*n.get_satellites_stats()),
                f'{n.vetting_progress():.2f}%'
            ])
        else:
            table.rows.append([ n.name, 'N/A', COLOR_PAIRS['offline'], 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A' ])

    table.columns.header = header
    table.rows.sort(header[0])
    return table, statistics

def show_banner():
    return figlet_format('Storj Nodes Summary', font='ogre', width=200)

def main():
    global COLOR_PAIRS

    nodes_path = '/etc/storj-utils/nodes.json'
    try:
        parseopt()
        with open(nodes_path) as f:
            nodes = json.loads(f.read())
    except FileNotFoundError as fnfe:
        print(fnfe)
        sys.exit(2)
    except Exception as err:
        print(err)
        print_usage()
        sys.exit(1)

    COLOR_PAIRS =   {
                        'online': colored(' Online ', 'green', Back),
                        'offline': colored(' Offline ', 'red', Back),
                        'yes': colored('Yes', 'green'),
                        'no': colored('No', 'red')
                    }



    StorjNodes = []
    for n in nodes:
        StorjNodes.append(StorjNode(n['name'], n['address'], n['port']))

    bottom_table, stats = summary_table(StorjNodes)
    info_table = general_info_table(stats)

    mid_table = BeautifulTable()
    mid_table.set_style(TABLE_STYLE)
    mid_table.border.left = ''
    mid_table.border.right = ''
    mid_table.border.top = ''
    mid_table.border.bottom = ''
    mid_table.columns.header = [colored(' GENERAL ', HEADER_TEXT_COLOR, Back), colored(' NODES ', HEADER_TEXT_COLOR, Back), colored(' DISK ', HEADER_TEXT_COLOR, Back), colored(' BANDWIDTH ', HEADER_TEXT_COLOR, Back), colored(' LEGEND ', HEADER_TEXT_COLOR, Back)]
    mid_table.rows.append(info_table)

    outer_table = BeautifulTable(maxwidth = TABLE_WIDTH)
    outer_table.set_style(TABLE_STYLE)
    outer_table.columns.header = [show_banner()]
    outer_table.rows.append([mid_table])
    outer_table.rows.append([bottom_table])
    outer_table.columns.padding_left[0] = 0
    outer_table.columns.padding_right[0] = 0
    print(outer_table)

if __name__ == '__main__':
    main()
