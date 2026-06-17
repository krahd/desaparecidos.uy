from desaparecidos.demo import create_demo_fixtures


def main() -> None:
    result = create_demo_fixtures()
    print(
        "Created synthetic demo fixtures: "
        f"{result['targets']} and {result['sources']}"
    )


if __name__ == "__main__":
    main()
