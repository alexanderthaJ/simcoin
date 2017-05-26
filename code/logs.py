import plan


def aggregate_logs(ids):
    commands = []
    timestamp_length = str(len('2016-09-22 14:46:41.706605'))
    logfile_raw = plan.log_file + '.raw'

    def prefix_lines(prefix):
        return 'sed -e \'s/^/' + prefix + ' /\''

    def remove_empty_lines():
        return 'sed "s/^$//g"'

    def remove_lines_starting_with_whitspace():
        return 'sed "s/^[[:space:]].*$//g"'

    def remove_multiline_error_messages():
        return 'sed "s/^.\{26\}  .*$//g"'

    def sed_command(_id): # insert node id after timestamp
        return 'sed "s/^.\{' + timestamp_length + '\}/& ' + _id + '/g"'

    "remove files from previous run"
    commands.append('rm -rf ' + plan.log_file)
    commands.append('rm -rf ' + logfile_raw)

    "consolidate logfiles from the nodes"
    commands.extend([' cat ' + plan.host_dir(_id) + '/regtest/debug.log '
                     ' |   ' + sed_command(_id) +
                     ' >>  ' + logfile_raw + '; '
                     for _id in ids])

    "clean the logfiles"
    commands.append(' cat ' + logfile_raw +
                    ' | ' + remove_empty_lines() +
                    ' | ' + remove_lines_starting_with_whitspace() +
                    ' | ' + remove_multiline_error_messages() +
                    ' > ' + plan.log_file
                    )
    "sort by timestamp"
    commands.append(' sort ' + plan.log_file)

    "aggregate fork information"
    commands.extend([' cat ' + plan.host_dir(_id) + '/chaintips.json '
                     ' | jq "length" '
                     ' | ' + prefix_lines(_id) +
                     ' >> ' + plan.root_dir + '/forks; '
                     for _id in ids])

    return commands