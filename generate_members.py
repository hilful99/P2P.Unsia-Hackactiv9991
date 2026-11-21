import csv
import random

random.seed(42)

first_names = [
    "Andi","Budi","Citra","Dewi","Eka","Fajar","Gita","Hendra","Indah","Joko",
    "Kartika","Luki","Maya","Nanda","Oky","Putri","Qori","Reza","Sari","Tono",
    "Umar","Vina","Wati","Xander","Yudi","Zahra","Agus","Bella","Cahyo","Dina",
    "Erwin","Fitri","Galih","Hana","Ivan","Jeni","Kevin","Lina","Miko","Nita",
    "Okta","Prima","Rina","Surya","Tari","Ucok","Vera","Wahyu","Yanti","Zaki",
    "Ayu","Bagas","Clara","Doni","Erika","Fauzi","Gilang","Hesti","Irwan","Jasmine",
    "Kurnia","Laras","Mulia","Niko","Oktavia","Pandu","Qila","Ridwan","Sintia","Teguh",
    "Ulfa","Vicky","Wulan","Yovan","Zara","Alif","Brenda","Chandra","Dita","Evan",
    "Fani","Guntur","Hilda","Iwan","Julia","Krisna","Leony","Marga","Nanang","Olivia",
    "Panji","Raisa","Sigit","Tiara","Udin","Vira","Wendy","Yoga","Zalfa","Arief"
]

last_names = [
    "Santoso","Wijaya","Kusuma","Pratama","Setiawan","Rahayu","Nugroho","Hidayat",
    "Permana","Saputra","Lestari","Wibowo","Purnama","Susanto","Utama","Halim",
    "Gunawan","Maulana","Firmansyah","Handoko","Anggraini","Budiman","Cahyadi",
    "Darmawan","Efendi","Firdaus","Ginting","Harahap","Iskandar","Junaidi"
]

provinces = [
    "DKI Jakarta","Jawa Barat","Jawa Tengah","Jawa Timur","DI Yogyakarta",
    "Banten","Bali","Sumatera Utara","Sumatera Selatan","Riau",
    "Kalimantan Timur","Sulawesi Selatan","Lampung","Nusa Tenggara Barat"
]

occupations = [
    "Karyawan Swasta","PNS / BUMN","Wirausaha / UMKM","Freelancer Digital",
    "Gig Worker / Ojol","Mahasiswa / Fresh Graduate","Guru / Dosen"
]

educations = [
    "SMA / SMK","Diploma (D3)","Sarjana (S1)","Magister (S2)","SD / SMP"
]

loan_purposes = [
    "Kebutuhan Sehari-hari","Pendidikan","Modal Usaha","Kesehatan",
    "Elektronik / Gadget","Renovasi Rumah","Liburan / Hiburan","Kendaraan"
]

default_statuses = [
    "Current-Performing","Special-Mention-DPD1-30","Substandard-DPD31-60",
    "Doubtful-DPD61-90","Default-Macet-TWP90"
]

root_causes = [
    "High-Interest-Rate-Compounding","Compulsive-FOMO-Spending",
    "Income-Shock-Underemployment","Gali-Lubang-Debt-Spiral","Speculative-Losses"
]

rows = []
used_names = set()
i = 0
while len(rows) < 100:
    fn = first_names[i % len(first_names)]
    ln = random.choice(last_names)
    full = f"{fn} {ln}"
    if full in used_names:
        ln = random.choice(last_names)
        full = f"{fn} {ln}"
    used_names.add(full)

    age = random.randint(18, 55)
    gender = random.choice(["Laki-laki", "Perempuan"])
    province = random.choice(provinces)
    education = random.choice(educations)
    occupation = random.choice(occupations)
    income = random.randint(2_000_000, 25_000_000)
    umr = random.choice([2_500_000, 2_950_000, 3_200_000, 3_800_000, 4_500_000, 5_000_000])
    num_apps = random.randint(1, 12)
    loan_amount = random.randint(1_000_000, 50_000_000)
    credit_limit = int(loan_amount * random.uniform(1.2, 2.5))
    tenor = random.choice([1, 3, 6, 9, 12])
    interest = round(random.uniform(0.20, 0.40), 2)
    purpose = random.choice(loan_purposes)
    dti = round(loan_amount / income, 2)
    dsr = round((loan_amount / tenor) / income, 4)
    util = round(loan_amount / credit_limit, 4)
    fdi = round(random.uniform(1.0, 9.5), 2)
    dpd = random.choice([0, 0, 0, 5, 10, 15, 25, 35, 45, 55, 70, 90, 120, 150, 180])

    if dpd == 0:
        status = "Current-Performing"
    elif dpd <= 30:
        status = "Special-Mention-DPD1-30"
    elif dpd <= 60:
        status = "Substandard-DPD31-60"
    elif dpd <= 90:
        status = "Doubtful-DPD61-90"
    else:
        status = "Default-Macet-TWP90"

    root = random.choice(root_causes)
    confidence = round(random.uniform(0.90, 0.99), 3)

    rows.append([
        f"MBR_{str(len(rows)+1).zfill(3)}",
        full,
        age, gender, province, education, occupation,
        income, umr, num_apps,
        loan_amount, credit_limit, tenor, interest, purpose,
        dti, round(income / umr, 2), util,
        round((loan_amount / tenor) * (1 + interest * 30), 0),
        dsr,
        income - round((loan_amount / tenor) * (1 + interest * 30), 0),
        dpd, fdi, status, root, confidence
    ])
    i += 1

headers = [
    "member_id","nama_lengkap","usia","gender","provinsi","pendidikan","pekerjaan",
    "pendapatan_bulanan_idr","umr_daerah_idr","jumlah_app_aktif",
    "total_pinjaman_idr","limit_kredit_idr","tenor_bulan","bunga_harian_pct","tujuan_pinjaman",
    "debt_to_income_ratio","income_to_umr_ratio","utilisasi_limit",
    "estimasi_cicilan_bulanan_idr","debt_service_ratio",
    "disposable_income_idr","days_past_due","financial_distress_index",
    "status_kredit","akar_masalah","confidence_score"
]

with open("d:/ibm/p2p/members_100.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(headers)
    writer.writerows(rows)

print(f"Generated {len(rows)} rows")
print("Saved to: members_100.csv")

# Print sample
import pandas as pd
df = pd.read_csv("d:/ibm/p2p/members_100.csv")
print(df[['member_id','nama_lengkap','usia','gender','provinsi','status_kredit']].head(10).to_string(index=False))
print()
print("Status distribution:")
print(df['status_kredit'].value_counts())
