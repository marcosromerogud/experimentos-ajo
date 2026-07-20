import asyncio
from playwright.async_api import async_playwright
import random


async def un_voto(p, indice: int, url_sala: str, valor_slider: int):
    """
    Realiza un único voto abriendo un navegador incógnito independiente.
    """
    print(f"\n🗳️  Voto {indice} - iniciando")

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
        # 1. Ir directo a la sala (URL directa, sin ingresar código)
        print(f"  🌐 [{indice}] Abriendo sala...")
        await page.goto(url_sala, wait_until='domcontentloaded')

        # 2. Esperar a que cargue la pregunta
        await asyncio.sleep(2)

        # 3. Seleccionar el valor en el slider (input type=range)
        slider = await page.wait_for_selector('input[type="range"]', timeout=5000)

        # Respetar los límites min/max del slider
        min_val = int(await slider.get_attribute('min') or 1)
        max_val = int(await slider.get_attribute('max') or 5)
        objetivo = max(min_val, min(valor_slider, max_val))

        # Setear el valor y disparar los eventos que escucha React
        await slider.evaluate(
            """(el, val) => {
                const setter = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype, 'value'
                ).set;
                setter.call(el, String(val));
                el.dispatchEvent(new Event('input', { bubbles: true }));
                el.dispatchEvent(new Event('change', { bubbles: true }));
            }""",
            objetivo,
        )

        valor_actual = await slider.input_value()
        print(f"  ✅ [{indice}] Slider en: {valor_actual}")

        # 4. Buscar botón de enviar/submit
        await asyncio.sleep(0.5)
        botones_submit = [
            'button[type="submit"]',
            'button:has-text("Votar")',
            'button:has-text("Submit")',
            'button:has-text("Enviar")',
            '[data-testid*="submit"]',
            '.submit-button',
        ]

        for selector in botones_submit:
            try:
                boton = await page.wait_for_selector(selector, timeout=1000)
                if boton:
                    await boton.click()
                    print(f"  📤 [{indice}] Voto enviado")
                    break
            except Exception:
                continue

        await asyncio.sleep(1)
        print(f"  ✅ [{indice}] Voto completado")
        return True

    except Exception as e:
        print(f"  ❌ [{indice}] Error: {str(e)}")
        return False

    finally:
        await browser.close()


async def votar_mentimeter(
    url_sala: str = "https://www.menti.com/alggkxgy4k8o?source=qr-page",
    cantidad: int = 10,
    valor_slider: int = 5,
    concurrencia: int = 3,
):
    """
    Vota automáticamente en Mentimeter en paralelo.

    - cantidad: total de votos a emitir.
    - concurrencia: cuántos navegadores votan al mismo tiempo.
    """
    semaforo = asyncio.Semaphore(concurrencia)

    async with async_playwright() as p:

        async def voto_con_limite(indice: int):
            async with semaforo:
                # Pequeño desfase para que no arranquen exactamente juntos
                await asyncio.sleep(random.uniform(0, 1))
                return await un_voto(p, indice, url_sala, valor_slider)

        tareas = [voto_con_limite(i + 1) for i in range(cantidad)]
        resultados = await asyncio.gather(*tareas)

    exitosos = sum(1 for r in resultados if r)
    print(f"\n🏁 Terminado: {exitosos}/{cantidad} votos exitosos")


# Ejecutar
if __name__ == "__main__":
    # CONFIGURACIÓN
    URL = "https://www.menti.com/alggkxgy4k8o?source=qr-page"  # URL directa de la sala
    VOTOS = 90             # Cantidad total de votos
    VALOR = 4              # Valor a marcar en el slider (1-5)
    CONCURRENCIA = 4         # Cuántos navegadores votan a la vez

    asyncio.run(votar_mentimeter(URL, VOTOS, VALOR, CONCURRENCIA))
