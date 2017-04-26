def fill_roa_struct(input, rad_tree, opener=default_opener):
    """
    Copy roa file into rad_tree.

    Max lenght is stored in data[asn]

    :param input: CSV file containing roa entries with columns:
        asn, prefix, max_length, validity
    :param rad_tree: Radix tree
    :return: Nothing
    """
    with opener(input) as roa_file:
        roa_reader = reader(roa_file, delimiter=',')
        for roa in roa_reader:  # roa : [asn, prefix, max_length, validity]
            if roa[3].lower() == "true":
                asn = int(roa[0])
                new_node = rad_tree.add(roa[1])
                new_node.data[asn] = max(new_node.data.get(asn, 0), int(roa[2]))
