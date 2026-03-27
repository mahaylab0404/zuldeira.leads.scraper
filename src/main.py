import asyncio
from apify import Actor
from playwright.async_api import async_playwright
from playwright_stealth import stealth_async

async def main():
    async with Actor:
        # 1. Fetch the inputs from your actor.json schema
        actor_input = await Actor.get_input() or {}
        queries = actor_input.get("searchQueries", ["nail salon Miami FL"])
        max_leads = actor_input.get("maxResults", 20)

        Actor.log.info(f"🚀 Initializing Zuldeira Lead Engine. Targets: {queries}")

        async with async_playwright() as p:
            # Launch browser (headless for speed, headful for debugging)
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            # Apply Stealth to bypass bot detection
            await stealth_async(page)

            for query in queries:
                Actor.log.info(f"🔎 Processing Query: {query}")
                
                # Navigate directly to the search results
                encoded_query = query.replace(" ", "+")
                await page.goto(f"https://www.google.com/maps/search/{encoded_query}", wait_until="networkidle")

                # Handle potential cookie consent (common in cloud environments)
                try:
                    await page.click("button[aria-label*='Accept']", timeout=3000)
                except:
                    pass

                leads_count = 0
                
                # Logic: Scroll to load results
                while leads_count < max_leads:
                    # Locate the results feed container
                    feed_selector = 'div[role="feed"]'
                    try:
                        await page.wait_for_selector(feed_selector, timeout=5000)
                    except:
                        Actor.log.error(f"Could not find results feed for {query}. Google might have changed the layout.")
                        break

                    # Scroll the feed container
                    await page.evaluate(f"document.querySelector('{feed_selector}').scrollBy(0, 800)")
                    await asyncio.sleep(2) # Natural pause to load content

                    # Extract business cards
                    # Note: These selectors change often. Inspect the 'aria-label' on the list items.
                    results = await page.locator('div[aria-label*="Results for"]').locator('a[href*="/maps/place/"]').all()
                    
                    if not results:
                        break

                    for result in results:
                        if leads_count >= max_leads:
                            break
                        
                        try:
                            # Extract data from the link's aria-label or child spans
                            title = await result.get_attribute("aria-label") or "Unknown Business"
                            link = await result.get_attribute("href")
                            
                            lead_data = {
                                "query": query,
                                "name": title,
                                "mapsUrl": link,
                                "location_context": "South Florida"
                            }

                            await Actor.push_data(lead_data)
                            leads_count += 1
                        except Exception as e:
                            continue

                Actor.log.info(f"✅ Finished {query}: Found {leads_count} leads.")

            await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
