"""Rules shared by the Streamlit games."""


def normalize_title(value: str) -> str:
    return " ".join(value.casefold().split())


def title_matches(guess: str, title: str) -> bool:
    return bool(normalize_title(guess)) and normalize_title(guess) == normalize_title(title)


def revenue_direction(first_revenue: int, second_revenue: int) -> str:
    if first_revenue == second_revenue:
        raise ValueError("Movies with equal revenue cannot form a round")
    return "higher" if second_revenue > first_revenue else "lower"
