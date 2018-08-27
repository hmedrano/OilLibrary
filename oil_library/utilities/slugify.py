
def slugify(str2slugify):
    separator = '_'
    return separator.join(str2slugify.lower().split())

def slugify_filename(str2slugify):
    separator = '_'    
    return separator.join(str2slugify.lower().replace('.','').split())    
