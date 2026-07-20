import asyncio
from playwright.async_api import async_playwright
import random

async def votar_mentimeter(codigo_sala: str = "39485617", opcion_buscar: str = "Claudia", cantidad: int = 10):
    """
    Vota automáticamente en Mentimeter.
    """

    for i in range(cantidad):
        print(f"\n🗳️  Voto {i + 1}/{cantidad}")

        async with async_playwright() as p:
            # Lanzar navegador
            browser = await p.chromium.launch(
                headless=False,
                args=[
                    '--incognito',
                    '--disable-blink-features=AutomationControlled',
                ]
            )

            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                locale='es-ES',
            )

            # Ocultar webdriver
            await context.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            """)

            page = await context.new_page()

            try:
                # 1. Ir a Mentimeter
                print("  🌐 Abriendo Mentimeter...")
                await page.goto('https://www.menti.com/', wait_until='domcontentloaded')
                await asyncio.sleep(0.5)

                # 2. Ingresar código
                print(f"  ⌨️  Ingresando código: {codigo_sala}")

                # Selector del input de código
                campo_codigo = await page.wait_for_selector('input[type="text"], input[placeholder*="code" i], input[placeholder*="código" i]', timeout=5000)
                await campo_codigo.fill(codigo_sala)
                await asyncio.sleep(0.3)

                # Presionar Enter para unirse
                await campo_codigo.press('Enter')

                # 3. Esperar a que cargue la pregunta
                print("  ⏳ Cargando pregunta...")
                await asyncio.sleep(2)

                # 4. Buscar y seleccionar la opción que contiene "Claudia"
                print(f"  🎯 Buscando opción: {opcion_buscar}")

                # Estrategia 1: Buscar por texto en los labels
                opcion_encontrada = False

                try:
                    # Buscar el label que contiene el texto Claudia
                    opcion = await page.locator(f'label:has-text("{opcion_buscar}")').first
                    await opcion.wait_for(timeout=3000)
                    await opcion.click()
                    print(f"  ✅ Opción '{opcion_buscar}' seleccionada")
                    opcion_encontrada = True
                except:
                    pass

                # Estrategia 2: Si no funciona, buscar por data-testid
                if not opcion_encontrada:
                    try:
                        # Buscar todos los inputs radio y sus labels asociados
                        opciones = await page.query_selector_all('input[type="radio"]')
                        for radio in opciones:
                            # Obtener el id del radio
                            radio_id = await radio.get_attribute('id')
                            # Buscar el label asociado
                            label = await page.query_selector(f'label[for="{radio_id}"]')
                            if label:
                                texto = await label.inner_text()
                                if opcion_buscar.lower() in texto.lower():
                                    await label.click()
                                    print(f"  ✅ Opción encontrada: {texto[:50]}...")
                                    opcion_encontrada = True
                                    break
                    except Exception as e:
                        print(f"  ⚠️ Error en estrategia 2: {e}")

                # Estrategia 3: Buscar por span con el texto
                if not opcion_encontrada:
                    try:
                        spans = await page.query_selector_all('span')
                        for span in spans:
                            texto = await span.inner_text()
                            if opcion_buscar.lower() in texto.lower():
                                # Subir al label padre
                                parent = await span.evaluate('el => el.closest("label")')
                                if parent:
                                    await page.click(f'label[for="{await parent.get_attribute("for")}"]')
                                    print(f"  ✅ Opción encontrada por span")
                                    opcion_encontrada = True
                                    break
                    except:
                        pass

                if not opcion_encontrada:
                    print("  ❌ No se encontró la opción")
                    await browser.close()
                    continue

                # 5. Buscar botón de enviar/submit si existe
                await asyncio.sleep(0.5)

                try:
                    # Posibles selectores de botón de enviar
                    botones_submit = [
                        'button[type="submit"]',
                        'button:has-text("Votar")',
                        'button:has-text("Submit")',
                        'button:has-text("Enviar")',
                        '[data-testid*="submit"]',
                        '.submit-button'
                    ]

                    for selector in botones_submit:
                        try:
                            boton = await page.wait_for_selector(selector, timeout=1000)
                            if boton:
                                await boton.click()
                                print("  📤 Voto enviado")
                                break
                        except:
                            continue

                except:
                    print("  ℹ️  No se encontró botón de submit (voto auto-guardado)")

                print("  ✅ Voto completado")
                await asyncio.sleep(1)

            except Exception as e:
                print(f"  ❌ Error: {str(e)}")

            finally:
                await browser.close()

        # Delay reducido entre votos
        delay = random.uniform(1, 2)
        print(f"  ⏱️  Esperando {delay:.1f}s...")
        await asyncio.sleep(delay)

# Ejecutar
if __name__ == "__main__":
    # CONFIGURACIÓN
    CODIGO = "39485617"      # Tu código sin espacios
    OPCION = "Ale"       # Texto a buscar
    VOTOS = 120             # Cantidad de votos

    asyncio.run(votar_mentimeter(CODIGO, OPCION, VOTOS))
