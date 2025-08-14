import csv
from collections import defaultdict

def read_transfer_data(filename):
    transfers=[]

    with open(filename,mode='r',encoding='utf-8') as file:
        reader=csv.DictReader(file)

        for row in reader:
            if row['price'].strip():
                try:
                    row['price']=float(row['price'])
                except ValueError:
                    row['price']=None

            transfers.append(row)
        return transfers
    
def generate_club_stats(transfers,clubs):

    postojeci_klubovi=set(t['to'] for t in transfers)
    nepostojeci=[c for c in clubs if c not in postojeci_klubovi]
    if nepostojeci:
        raise ValueError(f'Greska: Sledeci klubovi ne postoje u transfers datoteci:{','.join(nepostojeci)}')
    
    club_stats={}

    for club in clubs:
        club=club.strip()
        club_stats[club]=[]
    
    for transfer in transfers:
        to_club=transfer['to']
        if to_club in club_stats:
            player_info={
                'player':transfer['player'],
                'position':transfer['position'],
                'from':transfer['from']
            }
            club_stats[to_club].append(player_info)

    return club_stats

def write_club_stats(club_stats,output_file):
    with open(output_file,'w',encoding='utf-8') as f:
        for club,players in club_stats.items():
            f.write(f"{club}\n")
            for player in players:
                f.write(f" -{player['player']} ({player['position']}), from {player['from']}\n")

def calculate_league_stats(transfers):
    league_stats=defaultdict(lambda:{'count':0,'total_price':0.0})
    
    for transfer in transfers:
        league=transfer['league']
        price=transfer['price'] if transfer['price'] else 0.0

        league_stats[league]['count']+=1
        league_stats[league]['total_price']+=price

    sorted_stats=sorted(
        [(league,data['count'],data['total_price']) for league,data in league_stats.items()],
        key=lambda x:x[0]
    )
    return sorted_stats

def write_league_stats(league_stats,output_file):
    with open(output_file,'w',encoding='utf-8') as f:

        f.write('league,total_transfer_no,total_transfer_price\n')

        for league,count,total_price in league_stats:
            price_str=f"{int(total_price)}" if total_price.is_integer() else f"{total_price}"
            f.write(f"{league},{count},{price_str}\n")

def generisi_statistiku_po_poziciji(transferi,pozicija):

    postojece_pozicije=set(t['position'].lower() for t in transferi)
    if pozicija.lower() not in postojece_pozicije:
        raise ValueError(f'Greska: pogresno uneta pozicija {pozicija} po kojoj trazim je neispravna')


    statistika ={}

    for transfer in transferi:
        if transfer['position'].lower()==pozicija.lower():
            liga=transfer['league']
            sezona=transfer['season']
            igrac=transfer['player']

            if liga not in statistika:
                statistika[liga]={}

            if sezona not in statistika[liga]:
                statistika[liga][sezona]=[]

            statistika[liga][sezona].append(igrac)
        
    for liga in  statistika:
        for sezona in statistika[liga]:
            statistika[liga][sezona].sort()
        statistika[liga]=dict(sorted(statistika[liga].items()))

    redosled_liga=[]
    for transfer in transferi:
        liga=transfer['league']
        if liga not in redosled_liga:
            redosled_liga.append(liga)
    
    sortirana_statistika=[]
    for liga in redosled_liga:
        if liga in statistika:
            sortirana_statistika.append((liga,statistika[liga]))
    return sortirana_statistika

def upisi_statistiku(statistika,izlazna_txt):
    with open(izlazna_txt,'w',encoding='utf-8') as f:
        for liga,sezone in statistika:
            f.write(f'{liga}\n')
            for sezona,igraci in sezone.items():
                f.write(f"{sezona},{','.join(igraci)}\n")
            f.write('\n')

if __name__ == "__main__":
    transfers=read_transfer_data("transfer_data.csv")
    inputa=input("Enter you row to continue:")
    pozicija=input("Unesite pozisiju za koju zelite da vam dam tabelu:")
    clubs=[club.strip() for club  in inputa.split(',') if club.strip()]

    club_stats=generate_club_stats(transfers,clubs)
    write_club_stats(club_stats,'club_stat.txt')

    league_stats=calculate_league_stats(transfers)
    write_league_stats(league_stats,"league_stat.txt")

    statistika=generisi_statistiku_po_poziciji(transfers,pozicija)
    upisi_statistiku(statistika,'pos_stat.txt')