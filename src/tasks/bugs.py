BUGS = {
    "ordinal-teens": [
        ("if number % 100 in (11, 12, 13):", "if number % 10 in (11, 12, 13):"),
    ],
    "parameterize-unicode": [
        ("    normalized = unicodedata.normalize('NFKD', string)\n"
         "    return normalized.encode('ascii', 'ignore').decode('ascii')",
         "    return string.encode('ascii', 'ignore').decode('ascii')"),
        ("        string = re.sub(r'%s{2,}' % re_sep, separator, string)",
         "        string = re.sub(r'-{2,}', separator, string)"),
        ("        string = re.sub(r\"(?i)^{sep}|{sep}$\".format(sep=re_sep), '', string)",
         "        string = re.sub(r\"(?i)^-|-$\", '', string)"),
    ],
    "plural-rules": [
        ("    (r\"(?i)(x|ch|ss|sh)$\", r'\\1es'),", "    (r\"(?i)(x|ch)$\", r'\\1es'),"),
        ("    (r\"(?i)([^aeiouy]|qu)y$\", r'\\1ies'),", "    (r\"(?i)([^aeiouy]|qu)y$\", r'\\1ys'),"),
        ("    (r\"(?i)([lr])f$\", r'\\1ves'),\n", ""),
        ("    (r\"(?i)([^aeiouy]|qu)ies$\", r'\\1y'),", "    (r\"(?i)([^aeiouy]|qu)ies$\", r'\\1ie'),"),
    ],
    "plural-counterfactual": [
        ("    (r\"(?i)(x|ch|ss|sh)$\", r'\\1es'),", "    (r\"(?i)(x|ch)$\", r'\\1es'),"),
        ("    (r\"(?i)([^aeiouy]|qu)y$\", r'\\1ies'),", "    (r\"(?i)([^aeiouy]|qu)y$\", r'\\1ys'),"),
        ("    (r\"(?i)([^f])f$\", r'\\1ves'),\n", ""),
        ("    (r\"(?i)([^aeiouy]|qu)ies$\", r'\\1y'),", "    (r\"(?i)([^aeiouy]|qu)ies$\", r'\\1ie'),"),
    ],
    "acronym-support": [],
}
