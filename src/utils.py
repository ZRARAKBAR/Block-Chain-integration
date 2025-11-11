def truncate_hash(h, length=16):
    return (h[:length] + "...") if len(h) > length else h
