from data_parser.client.gologin_client.go_login_client import GoLoginClient


URL = (
    "https://en.bidfax.info/acura/rsx/page/2/"
)


def main():
    client = GoLoginClient("1")

    html = client.get_html(URL)

    print("\n========== HTML ==========")
    print(html)
    print("==========================")

    print("HTML length:", len(html))


if __name__ == "__main__":
    main()