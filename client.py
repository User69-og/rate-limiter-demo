import asyncio
import aiohttp
import time
import csv

async def fetch(session, url, results):
    start_time = time.time()
    try:
        async with session.get(url) as response:
            results.append((start_time, response.status))
    except Exception as e:
        # Catch connection errors if the server isn't running
        print(f"Connection failed: {e}")

async def main():
    url = "http://127.0.0.1:8000/api/data"
    results = []
    
    print("Starting load test...")
    async with aiohttp.ClientSession() as session:
        # Phase 1: Sudden Burst of 50 concurrent requests
        print("Sending initial burst of 50 requests...")
        tasks = [fetch(session, url, results) for _ in range(50)]
        await asyncio.gather(*tasks)
        
        # Phase 2: Sustained traffic (10 requests per second for 5 seconds)
        print("Sending sustained traffic (10 req/s)...")
        for _ in range(50):
            await asyncio.sleep(0.1) 
            await fetch(session, url, results)

    # Save data for plotting
    with open('results.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Timestamp", "Status"])
        writer.writerows(results)
        
    print("Test complete. Data saved to results.csv")

if __name__ == "__main__":
    asyncio.run(main())