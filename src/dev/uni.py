def matches_uniq_str(pre_str: str, str_list: list[str]) -> None | str:
    count = 0
    selected_name = ""

    for name in str_list:
        if name.startswith(pre_str):
            count += 1
            selected_name = name

    if count == 0:
        return None

    # pre_str is uniq to given name
    if count > 1:
        return ""

    return selected_name