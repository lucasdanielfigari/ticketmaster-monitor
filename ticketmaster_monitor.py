import asyncio
from datetime import datetime

from playwright.async_api import (
    async_playwright,
    TimeoutError as PlaywrightTimeoutError,
)


# ============================================================
# CONFIGURACIÓN
# ============================================================

PROFILE_DIR = r"C:\Users\user\Desktop\ticketmaster app\ticketmaster_profile"

CHECK_INTERVAL = 60  # segundos


# ============================================================
# EVENTOS
# ============================================================

EVENTS = [
    {
        "name": "Phoebe Bridgers — Dublin 23 Nov",
        "url": "https://www.ticketmaster.ie/phoebe-bridgers-dublin-23-11-2026/event/180064BBC954ED41",
        "type": "phoebe",
    },
    {
        "name": "Phoebe Bridgers — Dublin 24 Nov",
        "url": "https://www.ticketmaster.ie/phoebe-bridgers-dublin-24-11-2026/event/180064BBC956ED46",
        "type": "phoebe",
    },
    {
        "name": "Fontaines D.C. — Liverpool 20 Nov",
        "url": "https://www.ticketmaster.co.uk/fontaines-dc-liverpool-20-11-2026/event/3700650D190E9616",
        "type": "fontaines",
    },
    {
        "name": "Fontaines D.C. — Manchester 21 Nov",
        "url": "https://www.ticketmaster.co.uk/fontaines-dc-manchester-21-11-2026/event/1F006511B96E4B8A",
        "type": "fontaines",
    },
    {
        "name": "Fontaines D.C. — Glasgow 22 Nov",
        "url": "https://www.ticketmaster.co.uk/fontaines-dc-glasgow-22-11-2026/event/3600650DADDB2C32",
        "type": "fontaines",
    },
    {
        "name": "Fontaines D.C. — Leeds 24 Nov",
        "url": "https://www.ticketmaster.co.uk/fontaines-dc-leeds-24-11-2026/event/1F00650E8BCD43AD",
        "type": "fontaines",
    },
]


# ============================================================
# FONTAINES
# ============================================================

async def check_fontaines(page, url):

    print("   Abriendo página...")

    await page.goto(
        url,
        wait_until="domcontentloaded",
        timeout=60000,
    )

    print("   Esperando resultados...")

    # Ticketmaster necesita unos segundos para cargar
    # el estado de disponibilidad.
    await page.wait_for_timeout(20000)

    no_results = await page.get_by_text(
        "Sorry, we couldn't find any results",
        exact=True,
    ).count()

    if no_results > 0:
        return False

    return True


# ============================================================
# PHOEBE
# ============================================================

async def check_phoebe(page, url):

    print("   Abriendo página...")

    await page.goto(
        url,
        wait_until="domcontentloaded",
        timeout=60000,
    )

    # --------------------------------------------------------
    # Full Price Ticket
    # --------------------------------------------------------

    try:

        full_price = (
            page.get_by_role("listitem")
            .filter(has_text="Full Price Ticket")
            .first
        )

        await full_price.wait_for(
            timeout=30000
        )

    except PlaywrightTimeoutError:

        print(
            "   ⚠️ No apareció Full Price Ticket"
        )

        return None


    # --------------------------------------------------------
    # Quantity stepper
    # --------------------------------------------------------

    stepper = full_price.locator(
        '[data-testid="quantityStepper"]'
    )

    try:

        await stepper.wait_for(
            timeout=10000
        )

    except PlaywrightTimeoutError:

        print(
            "   ⚠️ No apareció quantity stepper"
        )

        return None


    # --------------------------------------------------------
    # Cantidad
    # --------------------------------------------------------

    try:

        spinbutton = stepper.locator(
            '[role="spinbutton"]'
        )

        quantity = await spinbutton.get_attribute(
            "aria-valuenow"
        )

        print(
            f"   Cantidad actual: {quantity}"
        )


        if quantity == "2":

            minus = stepper.locator(
                'button[class*="MinusButton"]'
            )

            if await minus.count() > 0:

                await minus.click(
                    force=True
                )

                await page.wait_for_timeout(
                    500
                )

                print(
                    "   Cantidad cambiada a 1"
                )

    except Exception as e:

        print(
            f"   ⚠️ Error cambiando cantidad: {e}"
        )


    # --------------------------------------------------------
    # Find Tickets
    # --------------------------------------------------------

    try:

        find_tickets = page.get_by_role(
            "button",
            name="Find Tickets",
        )

        await find_tickets.wait_for(
            timeout=10000
        )

        await find_tickets.click()

        print(
            "   Find Tickets → OK"
        )

    except PlaywrightTimeoutError:

        print(
            "   ⚠️ No apareció Find Tickets"
        )

        return None


    # --------------------------------------------------------
    # Event Information
    # --------------------------------------------------------

    try:

        await page.get_by_text(
            "Event Information",
            exact=True,
        ).wait_for(
            timeout=30000
        )

        print(
            "   Event Information → OK"
        )

    except PlaywrightTimeoutError:

        print(
            "   ⚠️ No apareció Event Information"
        )

        return None


    # --------------------------------------------------------
    # Checkbox de términos
    # --------------------------------------------------------

    terms_text = page.get_by_text(
        "I have read and agree to the above terms",
        exact=True,
    )

    if await terms_text.count() > 0:

        try:

            label = terms_text.locator(
                "xpath=ancestor::label[1]"
            )

            checkbox = label.locator(
                'input[type="checkbox"]'
            ).last

            checked = await checkbox.is_checked()

            if not checked:

                await label.click(
                    force=True
                )

                await page.wait_for_timeout(
                    300
                )

                print(
                    "   Términos → aceptados"
                )

        except Exception as e:

            print(
                f"   ⚠️ Error con checkbox: {e}"
            )

    else:

        print(
            "   Checkbox de términos no encontrado"
        )


    # --------------------------------------------------------
    # Proceed to Buy
    # --------------------------------------------------------

    try:

        proceed = page.get_by_role(
            "button",
            name="Proceed to Buy",
        )

        await proceed.wait_for(
            timeout=10000
        )

        await proceed.click()

        print(
            "   Proceed to Buy → OK"
        )

    except PlaywrightTimeoutError:

        print(
            "   ⚠️ No apareció Proceed to Buy"
        )

        return None


    # --------------------------------------------------------
    # Verified Resale Ticket
    # --------------------------------------------------------

    try:

        listings = page.get_by_text(
            "Verified Resale Ticket",
            exact=True,
        )

        # IMPORTANT:
        # Hay múltiples listings, por lo que usamos .first.
        await listings.first.wait_for(
            timeout=30000
        )

    except PlaywrightTimeoutError:

        print(
            "   ❌ No hay Verified Resale Ticket"
        )

        return False


    # --------------------------------------------------------
    # Contar listings
    # --------------------------------------------------------

    count = await listings.count()

    print(
        f"   Verified Resale Ticket: {count}"
    )

    return count > 0


# ============================================================
# COMPROBAR EVENTO
# ============================================================

async def check_event(context, event):

    page = await context.new_page()

    try:

        if event["type"] == "phoebe":

            return await check_phoebe(
                page,
                event["url"],
            )

        if event["type"] == "fontaines":

            return await check_fontaines(
                page,
                event["url"],
            )

        return None

    except Exception as e:

        print(
            f"   ⚠️ ERROR: {type(e).__name__}: {e}"
        )

        return None

    finally:

        await page.close()


# ============================================================
# MONITOR
# ============================================================

async def main():

    print(
        "=========================================="
    )

    print(
        "      TICKETMASTER RESALE MONITOR"
    )

    print(
        "=========================================="
    )

    print()

    print(
        f"Eventos: {len(EVENTS)}"
    )

    print(
        f"Intervalo: {CHECK_INTERVAL} segundos"
    )

    print()


    async with async_playwright() as p:

        # ----------------------------------------------------
        # Perfil persistente
        # ----------------------------------------------------

        context = await p.chromium.launch_persistent_context(
            PROFILE_DIR,
            headless=False,
        )


        # ----------------------------------------------------
        # Estado anterior
        # ----------------------------------------------------

        previous_state = {
            event["name"]: None
            for event in EVENTS
        }


        # ====================================================
        # LOOP INFINITO
        # ====================================================

        while True:

            print()

            print(
                "=========================================="
            )

            print(
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )

            print(
                "=========================================="
            )


            # ------------------------------------------------
            # Revisar cada evento
            # ------------------------------------------------

            for event in EVENTS:

                print()

                print(
                    f"→ {event['name']}"
                )


                available = await check_event(
                    context,
                    event,
                )


                # --------------------------------------------
                # DISPONIBLE
                # --------------------------------------------

                if available is True:

                    print(
                        "   🎟️ DISPONIBILIDAD DETECTADA"
                    )


                    if previous_state[
                        event["name"]
                    ] is False:

                        print(
                            "   🚨 CAMBIO: NO → SÍ"
                        )


                # --------------------------------------------
                # NO DISPONIBLE
                # --------------------------------------------

                elif available is False:

                    print(
                        "   ❌ Sin tickets"
                    )


                # --------------------------------------------
                # ERROR
                # --------------------------------------------

                else:

                    print(
                        "   ⚠️ No se pudo determinar"
                    )


                # --------------------------------------------
                # Actualizar estado
                # --------------------------------------------

                if available is not None:

                    previous_state[
                        event["name"]
                    ] = available


            # ------------------------------------------------
            # Esperar próximo ciclo
            # ------------------------------------------------

            print()

            print(
                f"Esperando {CHECK_INTERVAL} segundos..."
            )

            await asyncio.sleep(
                CHECK_INTERVAL
            )


# ============================================================
# EJECUTAR
# ============================================================

if __name__ == "__main__":

    asyncio.run(main())