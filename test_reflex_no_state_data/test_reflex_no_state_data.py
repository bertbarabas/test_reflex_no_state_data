from pydantic import BaseModel, computed_field

import reflex as rx


# MODEL
class PaintColor(BaseModel):
    brand: str
    code: str
    name: str
    hex_code: str

    @computed_field
    @property
    def id(self) -> str:
        return f"{self.brand}-{self.code}".lower().replace(" ", "_")


class PaintSchemeElement(BaseModel):
    element_name: str
    paint_color_ids: list[str]


class PaintScheme(BaseModel):
    name: str
    sub_title: str
    notes: list[str]
    elements: list[PaintSchemeElement]


class PaintSchemeCatalog(BaseModel):
    catalog_name: str
    paint_schemes: dict[str, PaintScheme] = {}
    paint_colors: dict[str, PaintColor] = {}


def _create_approved_catalog() -> PaintSchemeCatalog:
    brand = "Sherwin Williams"
    colors = [
        PaintColor(
            brand=brand, code="SW 6336", name="Nearly Peach", hex_code="#EBDCCF"
        ),
        PaintColor(brand=brand, code="SW 7006", name="Extra White", hex_code="#EEECE7"),
        PaintColor(
            brand=brand, code="SW 6050", name="Abalone Shell", hex_code="#D9CAC1"
        ),
        PaintColor(brand=brand, code="N/A", name="ANY IN SCHEME", hex_code="N/A"),
    ]

    catalog = PaintSchemeCatalog(
        catalog_name="Approved Paint Schemes", paint_colors={c.id: c for c in colors}
    )

    elements = [
        PaintSchemeElement(element_name="Body", paint_color_ids=[colors[0].id]),
        PaintSchemeElement(element_name="Front Door", paint_color_ids=[colors[1].id]),
        PaintSchemeElement(element_name="Fascia", paint_color_ids=[colors[2].id]),
        PaintSchemeElement(element_name="Accent", paint_color_ids=[colors[2].id]),
        PaintSchemeElement(element_name="Garage Door", paint_color_ids=[colors[3].id]),
    ]

    catalog.paint_schemes["40R"] = PaintScheme(
        name="40R", sub_title="", notes=[], elements=elements
    )
    return catalog


_approved_paint_schemes = _create_approved_catalog()

paint_scheme_catalogs = {_approved_paint_schemes.catalog_name: _approved_paint_schemes}


# STATE
class PaintSchemeSelectionState(rx.State):
    selected_paint_scheme_catalog_name: str = "Approved Paint Schemes"
    paint_scheme_catalogs: dict[str, PaintSchemeCatalog] = paint_scheme_catalogs

    @rx.var
    def selected_paint_scheme_catalog(self) -> PaintSchemeCatalog:
        return self.paint_scheme_catalogs[self.selected_paint_scheme_catalog_name]


#  UI
def paint_color_card_widget(
    paint_color: PaintColor,
    on_click_event: rx.event | None = None,
    on_double_click_event: rx.event | None = None,
) -> rx.Component:
    return rx.box(
        rx.button(
            paint_color_card(paint_color=paint_color),
            id=paint_color.id,
            variant="ghost",
            on_click=on_click_event,
            on_double_click=on_double_click_event,
            type="button",
            _hover={
                "box-shadow": "0 0 0 1px gray",
            },
            _focus={
                "box-shadow": f"0 0 0 1px {rx.color('accent', 9)}",
                "outline": "none",
            },
            border_radius="10px",
            padding="0px",
        ),
        padding_top="10px",
        padding_bottom="10px",
        padding_left="15px",
        padding_right="15px",
    )


def paint_color_card(paint_color: PaintColor) -> rx.Component:
    return rx.card(
        rx.vstack(
            rx.box(
                background_color=paint_color.hex_code,
                width="100%",
                height="100px",
            ),
            rx.vstack(
                rx.text(paint_color.brand),
                rx.text(paint_color.name),
                rx.text(paint_color.code),
                spacing="0",
                padding="0.25em",
            ),
            spacing="0",
        ),
        border_radius="3px",
        padding="1em",
        min_width="10em",
    )


def paint_color_scheme_element(
    paint_scheme_catalog: PaintSchemeCatalog, paint_scheme_element: PaintSchemeElement
) -> rx.Component:
    return rx.vstack(
        rx.text(
            paint_scheme_element.element_name,
            align="center",
            width="100%",
        ),
        rx.hstack(
            rx.foreach(
                paint_scheme_element.paint_color_ids,
                lambda paint_color_id: paint_color_card_widget(
                    paint_color=paint_scheme_catalog.paint_colors[paint_color_id],
                ),
            ),
        ),
        spacing="0",
    )


def paint_color_scheme(
    paint_scheme_name: str, paint_scheme_catalog: PaintSchemeCatalog
) -> rx.Component:
    paint_scheme = paint_scheme_catalog.paint_schemes[paint_scheme_name]
    return rx.vstack(
        rx.text(paint_scheme.name),

        # ---------------------------------------------------------------------
        # If you comment this part out, even the non-state data structure works
        # So it can handle getting all of:
        # 
        # paint_scheme_catalog.paint_schemes[paint_scheme_name].name
        # 
        # but it cannot get other nested elements.
        rx.hstack(
            rx.foreach(
                paint_scheme.elements,
                lambda paint_scheme_element: paint_color_scheme_element(
                    paint_scheme_catalog, paint_scheme_element
                ),
            )
        ),
        # ---------------------------------------------------------------------

        background=rx.color(color="gray", shade=3),
        padding="1em",
    )


def index() -> rx.Component:
    return rx.container(
        rx.vstack(
            rx.heading(
                "Generate exception when showing nested data structures directly instead of via State"
            ),
            # Below Works
            paint_color_scheme(
                "40R", PaintSchemeSelectionState.selected_paint_scheme_catalog
            ),
            # ---------------------------------------------------------------------
            #  Below causes exception (uncomment it to try)
            # paint_color_scheme("40R", paint_scheme_catalogs["Approved Paint Schemes"]),
            # ---------------------------------------------------------------------
            padding="1em",
        ),
    )


app = rx.App()
app.add_page(index)
