import reflex as rx

config = rx.Config(
    app_name="test_reflex_no_state_data",
    plugins=[
        rx.plugins.RadixThemesPlugin(),
    ],
    disable_plugins=[
        rx.plugins.SitemapPlugin(),
    ],
)
