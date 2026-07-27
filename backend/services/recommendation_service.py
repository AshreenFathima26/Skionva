class RecommendationEngine:
    def __init__(self, weather, conditions, score):
        self.weather=weather
        self.conditions=[c.lower() for c in conditions]
        self.score=score
        self.result={"health_status":"","summary":"","morning":[],"afternoon":[],"night":[],"weekly":[],"diet":[],"ingredients":[],"warnings":[],"reasons":[]}
    def add(self,s,v):
        if v not in self.result[s]:
            self.result[s].append(v)
    def defaults(self):
        [self.add("morning",x) for x in ["Gentle Cleanser","Vitamin C Serum","Lightweight Moisturizer","SPF 50 Sunscreen"]]
        [self.add("afternoon",x) for x in ["Drink water","Reapply sunscreen","Avoid touching face","Face mist if required"]]
        [self.add("night",x) for x in ["Cleanse skin","Niacinamide Serum","Moisturizer","Sleep 7-8 hours","Lip balm"]]
        [self.add("diet",x) for x in ["Drink 2.5-3L water","Eat fruits","Leafy vegetables","Reduce sugar","Exercise 30 minutes"]]
        [self.add("weekly",x) for x in ["Hydrating mask","Exfoliate once a week","Wash pillow covers","Clean makeup brushes","Review progress"]]
        [self.add("ingredients",x) for x in ["Vitamin C","Niacinamide","Ceramides","Hyaluronic Acid"]]
        [self.add("warnings",x) for x in ["Never skip sunscreen","Avoid harsh scrubbing","Patch test new products","Remove makeup before sleep"]]
    def weather_rules(self):
        t=self.weather.get("temperature",30);h=self.weather.get("humidity",60);uv=self.weather.get("uv",5)
        if uv>=8:
            self.add("morning","Wear sunglasses");self.add("afternoon","Reapply SPF every 2 hours");self.add("warnings","Avoid direct noon sunlight");self.add("reasons","High UV index")
        if t>=32:
            self.add("diet","Increase water intake");self.add("diet","Eat watermelon");self.add("reasons","Hot weather")
        if h>=75:
            self.add("morning","Oil-free cleanser");self.add("morning","Gel moisturizer");self.add("reasons","High humidity")
    def condition_rules(self):
        m={"acne":[("night","Salicylic Acid"),("ingredients","Salicylic Acid"),("warnings","Do not squeeze pimples"),("reasons","Acne detected")],
        "dryness":[("night","Ceramide cream"),("ingredients","Glycerin"),("reasons","Dry skin detected")],
        "oiliness":[("weekly","Clay mask"),("ingredients","Green Tea Extract"),("reasons","Oily skin detected")],
        "pigmentation":[("night","Alpha Arbutin"),("ingredients","Alpha Arbutin"),("reasons","Pigmentation detected")],
        "darkcircles":[("night","Caffeine Eye Cream"),("ingredients","Peptides"),("reasons","Dark circles detected")],
        "pores":[("weekly","BHA exfoliant"),("ingredients","BHA"),("reasons","Visible pores")]}
        for c in self.conditions:
            if c in m:
                for sec,val in m[c]:
                    self.add(sec,val)
    def score_rules(self):
        self.result["health_status"]="Excellent" if self.score>=90 else "Healthy" if self.score>=80 else "Moderate" if self.score>=70 else "Needs Attention"
    def summary(self):
        self.result["summary"]=f"Today's Glowee analysis indicates {self.result['health_status']} skin. Continue your skincare routine, stay hydrated, use sunscreen daily, and follow the weekly care plan."
    def generate(self):

        self.defaults()

        self.weather_rules()

        self.condition_rules()

        self.score_rules()

        self.summary()

        print("INGREDIENTS =>", self.result["ingredients"])
        return self.result