from django import template

register = template.Library()


@register.filter
def arabic_num(num):
    western = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    eastern = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩']
    try:
        s = str(num)
        for w, e in zip(western, eastern):
            s = s.replace(w, e)
        return s
    except Exception:
        return num


@register.filter
def arabic_num_filter(num):
    return arabic_num(num)
