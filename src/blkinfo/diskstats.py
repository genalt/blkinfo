"""Module to get disk statistic for all disks enumerated in /proc/diskstats"""
STAT_FILE = '/proc/diskstats'

# fields appears in the list in the exact order
# see https://www.kernel.org/doc/Documentation/ABI/testing/procfs-diskstats
STAT_FIELDS = ['major', 'minor', 'kname', 'reads_completed', 'reads_merged', 'sectors_read', 'time_spent_reading_ms',
               'writes_completed', 'writes_merged', 'sectors_written', 'time_spent_ writing', 'ios_in_progress',
               'time_spent_doing_ios_ms', 'weighted_time_ios_ms']


def get_disk_stats():
    """This function parses disk statistic fields in /proc/diskstats
    and return a dictionary"""

    statistics = {}

    with open(STAT_FILE) as stat_f:
        lines = stat_f.read().split('\n')

        for line in lines:
            values = [v for v in line.split(' ') if v != '']
            if len(values) < len(STAT_FIELDS):
                continue
            statistics[values[2]] = dict(zip(STAT_FIELDS, values))

    return statistics
