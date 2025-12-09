import json
from pprint import pprint

if __name__ == "__main__":
    a = """"emojis":{},"streamingChannelId":"f00f6d46ecc6d735b96ecf376b9e5212","donationId":"49Pek68nxMhgqYPhVRhZ6MV0VhkmT","donationType":"CHAT","weeklyRankList":[{"userIdHash":"d2c399f32cc26f3d32969b493d20b24d","nickName":"아니니","verifiedMark":false,"activatedAchievementBadgeIds":[],"donationAmount":300000,"ranking":1},{"userIdHash":"84d817d7457adcda071d1a9948e4aa97","nickName":"한그릇","verifiedMark":false,"activatedAchievementBadgeIds":[],"donationAmount":130000,"ranking":2},{"userIdHash":"6697722166eb00d399d434a6548d7231","nickName":"니니아사랑단","verifiedMark":false,"activatedAchievementBadgeIds":[],"donationAmount":30000,"ranking":3},{"userIdHash":"ab48b22f0214219ed4226b5765078611","nickName":"차한잔하겠어","verifiedMark":false,"activatedAchievementBadgeIds":[],"donationAmount":4000,"ranking":4},{"userIdHash":"f6edb2eef6e9ccde6c36dfb545b17707","nickName":"Mad싱어","verifiedMark":false,"activatedAchievementBadgeIds":[],"donationAmount":3000,"ranking":5},{"userIdHash":"5505aebcae5000f34b3788e89fa26a46","nickName":"히바리쿄야","verifiedMark":false,"activatedAchievementBadgeIds":[],"donationAmount":3000,"ranking":6},{"userIdHash":"3eb4a0665ef2b56dd16c8a6e1eb132f6","nickName":"검은콩칼국수","verifiedMark":false,"activatedAchievementBadgeIds":[],"donationAmount":2000,"ranking":7},{"userIdHash":"24aafa1959f09eaf40495260187df3d7","nickName":"Rbno","verifiedMark":false,"activatedAchievementBadgeIds":[],"donationAmount":1000,"ranking":8},{"userIdHash":"2c16c6b1029dba512f0c72dad3d10277","nickName":"만패 왕","verifiedMark":false,"activatedAchievementBadgeIds":[],"donationAmount":1000,"ranking":9},{"userIdHash":"7bc7c5edd2bb9f35c9403b48a775050d","nickName":"준십이","verifiedMark":false,"activatedAchievementBadgeIds":[],"donationAmount":1000,"ranking":10}],"isAnonymous":true,"payType":"CURRENCY","payAmount":1000,"osType":"PC","continuousDonationDays":0,"chatType":"STREAMING"}'"""
    
    pprint(json.loads(a))

    with open("Private//Headers.json", encoding="utf-8") as f:
        HEADERS = json.load(f)
        pprint(HEADERS)
        
