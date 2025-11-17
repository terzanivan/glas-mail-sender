from string import Template


# Provide the template protperty-value mapping in kwargs; returns a fill in mail template
def PrepareMail(t: Template, **kwargs) -> str:
    for identifier in t.get_identifiers():
        if identifier not in kwargs.keys():
            raise KeyError(f"key:{identifier} expected but not found in {kwargs}")
    return t.substitute(kwargs)
