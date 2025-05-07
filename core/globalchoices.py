CUSTOMER_RANK_CHOICES = [
    ("1", "Noob")
]

SELLER_RANK_CHOICES = [
    ("1", "Noob")
]

DELIVERYBOY_RANK_CHOICES = [
    ("1", "Noob")
]

STATE_CHOICES = [
    ("TN", "Tamil Nadu"),
    ("KL", "Kerala"),
]

DISTRICT_CHOICES = [
    # Tamil Nadu Districts
    ("AR", "Ariyalur"),
    ("CH", "Chennai"),
    ("CO", "Coimbatore"),
    ("CU", "Cuddalore"),
    ("DH", "Dharmapuri"),
    ("DI", "Dindigul"),
    ("EK", "Erode"),
    ("KA", "Kallakurichi"),
    ("KA2", "Kancheepuram"),
    ("KA3", "Kanniyakumari"),
    ("KA4", "Karur"),
    ("KR", "Krishnagiri"),
    ("MA", "Madurai"),
    ("NA", "Nagapattinam"),
    ("NI", "Nilgiris"),
    ("PE", "Perambalur"),
    ("PU", "Pudukkottai"),
    ("RA", "Ramanathapuram"),
    ("SA", "Salem"),
    ("SI", "Sivaganga"),
    ("TE", "Tenkasi"),
    ("TH", "Thanjavur"),
    ("TH2", "Theni"),
    ("TH3", "Thoothukudi"),
    ("TI", "Tiruchirappalli"),
    ("TI2", "Tirunelveli"),
    ("TI3", "Tirupathur"),
    ("TI4", "Tiruppur"),
    ("TI5", "Tiruvallur"),
    ("TI6", "Tiruvannamalai"),
    ("TV", "Tiruvarur"),
    ("VE", "Vellore"),
    ("VI", "Viluppuram"),
    ("VI2", "Virudhunagar"),

    # Kerala Districts
    ("AL", "Alappuzha"),
    ("ER", "Ernakulam"),
    ("ID", "Idukki"),
    ("KA", "Kannur"),
    ("KA2", "Kasaragod"),
    ("KO", "Kollam"),
    ("KO2", "Kottayam"),
    ("KO3", "Kozhikode"),
    ("MA", "Malappuram"),
    ("PA", "Palakkad"),
    ("PA2", "Pathanamthitta"),
    ("TH", "Thiruvananthapuram"),
    ("TH2", "Thrissur"),
    ("WA", "Wayanad"),
]

PRODUCTS_CHOICES = [
    ("GROCERY", "Grocery"),
    ("FOOD", "Food"),
    ("DESSERTS", "Desserts"),
]


COLOR_CHOICES = [
    ("RED", "Red"), 
    ("YELLOW", "Yellow")
]

RATING_CHOICES = [(str(i), str(i)) for i in range(1, 6)]

ORDER_STATUS_CHOICES = [
    ("P", "Pending"),
    ("OC","Order Confirmed"),
    ("S", "Shipped"),
    ("O", "Out for Delivery"),
    ("D", "Delivered"),
    ("C", "Cancelled"),
]
