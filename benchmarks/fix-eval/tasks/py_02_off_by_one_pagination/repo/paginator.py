def paginate(items: list, page: int, page_size: int) -> dict:
    if page_size <= 0:
        raise ValueError("page_size must be positive")
    total = len(items)
    total_pages = total // page_size
    if page < 1:
        page = 1
    start = (page - 1) * page_size
    end = start + page_size - 1
    return {
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "items": items[start:end],
    }
