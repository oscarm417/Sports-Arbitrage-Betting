# Sports-Arbitrage-Betting
Finds all betting arbitrage opportunities across all major sports betting companies. Currently only a report of the bets is outputted. Future projects consists of automatically sending the orders to the corresponding exchange.  Another future improvement is adjusting the bet sizes to hide arbitrage behavior. For example, putting a bet size of 89.72 is very odd, so we will have to round up or find a multiplier that makes it a round number, which ever has less of an impact on the final profit.


![image](https://user-images.githubusercontent.com/65280357/205215899-bb5810b3-a9d4-4b2f-adc7-836cae4f7bdc.png)


![image](https://user-images.githubusercontent.com/65280357/205215848-d7e40cd4-cd6b-47dd-8242-f599c5ce334d.png)

It outputs bets that add up to less than 100%. Most of these arbitrage bets will yield around .25 to 2% returns. 
You can calculte youll profit by the following formula: Bet_amount/sum([odds from betting on all outcomes]). 

The next step in the project is automatically creating the optimal bet size for each leg of the bet. Additionally, it will adjust the bet to maximize profits while minimizing odd size bets......

