from firecrawl import Firecrawl

firecrawl = Firecrawl(api_key="fc-9055effbd7fd45c89c4d70387e4c84f3")

doc = firecrawl.scrape("https://www.krushikranti.com/bajarbhav/kanda-bajar-bhav-today",
                       formats=[{
                           "type": "json",
                           "prompt": "Extract the max and min prices of onion in sangamner, lasalgaon, nashik, sinnar (its mentioned on the site in Marathi language)."
                       }],
                        only_main_content=False,
                        timeout=120000
                    )

print(doc)