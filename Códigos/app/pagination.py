from flask import request


def page_options():
    return max(1, request.args.get('page', 1, type=int)), min(100, max(1, request.args.get('page_size', 20, type=int)))


def page_info(page, size, total):
    pages = max(1, (total + size - 1) // size)
    return dict(page=min(page, pages), page_size=size, total=total, pages=pages)
