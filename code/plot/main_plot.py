import matplotlib.pyplot as plt


def plot_scatter(filename, variable_key_selected):
    with open(filename, 'r') as f:
        str_data = f.read()
    dict_data = eval(str_data)
    # print(dict_data)

    dict_apps = {}
    dict_data_rearranged = {}
    for key in dict_data.keys():
        app_key, variable_key = key.split('+')
        if app_key not in dict_apps.keys():
            dict_apps[app_key] = 0
        if variable_key in dict_data_rearranged.keys():
            dict_data_rearranged[variable_key].append(dict_data[key])
        else:
            dict_data_rearranged[variable_key] = [dict_data[key]]
    print(dict_data_rearranged)

    plt.figure()
    plt.xlabel('Apps')
    plt.ylabel('F1-score')
    plt.xticks(range(len(dict_apps.keys())), dict_apps.keys())
    plt.xlim([-0.5, len(dict_apps.keys()) + 1])
    plt.grid(axis='y')
    for variable_key in dict_data_rearranged.keys():
        if variable_key == variable_key_selected:
            plt.scatter(
                range(len(dict_apps.keys())),
                dict_data_rearranged[variable_key],
                label=variable_key,
                marker='x',
                s=100
            )
        else:
            plt.scatter(
                range(len(dict_apps.keys())),
                dict_data_rearranged[variable_key],
                label=variable_key,
                marker='+',
                s=50
            )
    plt.legend()
    plt.show()


def plot_line(filename, x_label):
    with open(filename, 'r') as f:
        str_data = f.read()
    dict_data = eval(str_data)
    # print(dict_data)

    dict_variables = {}
    dict_data_rearranged = {}
    for key in dict_data.keys():
        app_key, variable_key = key.split('+')
        if variable_key not in dict_variables.keys():
            dict_variables[variable_key] = 0
        if app_key in dict_data_rearranged.keys():
            dict_data_rearranged[app_key].append(dict_data[key])
        else:
            dict_data_rearranged[app_key] = [dict_data[key]]
    print(dict_data_rearranged)

    plt.figure()
    plt.xlabel(x_label)
    plt.ylabel('F1-score')
    plt.xticks(range(len(dict_variables.keys())), dict_variables.keys())
    plt.xlim([-0.5, len(dict_variables.keys()) + 1])
    plt.grid(axis='y')
    for variable_key in dict_data_rearranged.keys():
        plt.plot(
            range(len(dict_variables.keys())),
            dict_data_rearranged[variable_key],
            label=variable_key,
            marker='x',
        )
    plt.legend()
    plt.show()


def plot_box(filename, x_label):
    with open(filename, 'r') as f:
        str_data = f.read()
    dict_data = eval(str_data)
    # print(dict_data)

    dict_data_rearranged = {}
    for key in dict_data.keys():
        app_key, variable_key = key.split('+')
        if variable_key in dict_data_rearranged.keys():
            dict_data_rearranged[variable_key].append(dict_data[key])
        else:
            dict_data_rearranged[variable_key] = [dict_data[key]]
    print(dict_data_rearranged)

    plt.figure()
    plt.xlabel(x_label)
    plt.ylabel('F1-score')
    plt.xticks(size=8)
    data_plot = []
    for variable_key in dict_data_rearranged.keys():
        data_plot.append(dict_data_rearranged[variable_key])
    plt.boxplot(
        data_plot,
        labels=dict_data_rearranged.keys(),
    )
    plt.show()


if __name__ == '__main__':
    # plot_scatter('classifiers.txt', 'RF')
    # plot_line('classifiers.txt')

    plot_line('classifiers.txt', 'Classifiers')
    plot_box('classifiers.txt', 'Classifiers')

    plot_line('resampling_filters.txt', 'Resampling filters')
    plot_box('resampling_filters.txt', 'Resampling filters')

    plot_line('target_resolutions.txt', 'Target resolutions')
    plot_box('target_resolutions.txt', 'Target resolutions')