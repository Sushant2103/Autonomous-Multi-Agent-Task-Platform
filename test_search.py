from tools.search_tool import search_web


query = input(
    "Enter something to search: "
)

results = search_web(
    query,
    max_results=5
)


print("\n==============================")
print(" REAL WEB SEARCH RESULTS")
print("==============================")


for index, result in enumerate(
    results,
    start=1
):

    print(
        f"\n{index}. {result['title']}"
    )

    print(
        f"URL: {result['url']}"
    )

    print(
        f"\n{result['content'][:500]}"
    )

    print(
        "\n------------------------------"
    )