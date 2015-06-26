import csv

### Переменные для более понятной индексации
bm = 0
sm = 1
bl = 2
sl = 3

v = 1
p = 2

### Списки для заявок и сделок
bids = [list([]) for _ in range(4)]
deals = []
fileName = 'Код МОЕХ-разработка-Зимин Степан Михайлович.csv'


def moex_main():    
    read_and_sort("MoEx_exmpl_filled.csv")    
    if bids[bl][0][p] < bids[sl][0][p]:     ### проверка на пересечение цен               
        with open(fileName, 'w') as file:
            file.write('FAILED')
    else:        
        result = make_deals()
        write_to_file(result)
        
    
def read_and_sort(name):
    try:
        file = open(name)                   ### проверка на существование файла  
    except FileNotFoundError:
        with open(fileName, 'w') as file:
            file.write('FAILED')
        exit()       
    listOfBids = csv.reader(file, delimiter = ';')
    
    for newBid in listOfBids:
        try:
            num = int(newBid[0])
            vol = int(newBid[3])

            if len(newBid) > 5 or num < 1 or vol < 0:   ### проверка на неотрицательность полей     
                continue
        
            if newBid[2] == 'M':
                if newBid[1] == 'S':
                    bids[sm].append((num, vol))
                elif newBid[1] == 'B':
                    bids[bm].append((num, vol))
            elif newBid[2] == 'L':
                price = int(newBid[4])
                if price < 0:
                    continue
                if newBid[1] == 'S':
                    bids[sl].append((num, vol, price))
                elif newBid[1] == 'B':
                    bids[bl].append((num, vol, price))

        except ValueError:
            continue
        except IndexError:
            continue

    if len(bids[bl]) == 0 or len(bids[sl]) == 0:    ### проверка, есть ли лимитные заявки 
        with open(fileName, 'w') as file:
            file.write('FAILED')
            exit(file)
     
    bids[bl].sort(key=lambda objct: objct[2], reverse=True) ### сортировка 
    bids[sl].sort(key=lambda objct: objct[2])
    

def make_deals():
    maxValue = 0
    currentVolume = 0
    currentPrice = bids[bl][0][p]
    counterBuy = 0      ### Указатели на текущую сводимую сделку   
    counterSell = 0

    optPrice = currentPrice
    maxValueNum = 0

    marketBuy = len(bids[bm]) > 0
    marketSell = len(bids[sm]) > 0

    while True:

        if marketBuy:   ### проверка на пересечение цен   
            typeBuy = bm
        else:
            typeBuy = bl

        if marketSell:
            typeSell = sm
        else:
            typeSell = sl

        if not marketBuy and not marketSell:        ### если сводятся лимитные сделки, а текущая цена на покупку меньше, чем на продажу, то останавливаемся 
            if bids[typeBuy][counterBuy][p] < bids[typeSell][counterSell][p]:
                break
            elif currentPrice > bids[typeBuy][counterBuy][p]: ### если рыночная цена больше, чем текущая цена на покупку, то понижаем ее
                currentPrice = bids[typeBuy][counterBuy][p]

        tempBuyNum = bids[typeBuy][counterBuy][0]
        tempSellNum = bids[typeSell][counterSell][0]

        if bids[typeBuy][counterBuy][v] < bids[typeSell][counterSell][v]:  ### сводим две заявки в сделку
            tempVolume = bids[typeBuy][counterBuy][v]
            currentVolume += bids[typeBuy][counterBuy][v]
            if typeSell == sm:
                bids[typeSell][counterSell] = (bids[typeSell][counterSell][0], bids[typeSell][counterSell][v] - bids[typeBuy][counterBuy][v])
            else:
                bids[typeSell][counterSell] = (bids[typeSell][counterSell][0], bids[typeSell][counterSell][v] - bids[typeBuy][counterBuy][v], bids[typeSell][counterSell][p])
            counterBuy += 1
        elif bids[typeBuy][counterBuy][v] > bids[typeSell][counterSell][v]:
            tempVolume = bids[typeSell][counterSell][v]
            currentVolume += bids[typeSell][counterSell][v]
            if typeBuy == bm:
                bids[typeBuy][counterBuy] = (bids[typeBuy][counterBuy][0], bids[typeBuy][counterBuy][v] - bids[typeSell][counterSell][v])
            else:
                bids[typeBuy][counterBuy] = (bids[typeBuy][counterBuy][0], bids[typeBuy][counterBuy][v] - bids[typeSell][counterSell][v], bids[typeBuy][counterBuy][p])
            counterSell += 1
        else:
            tempVolume = bids[typeSell][counterSell][v]
            currentVolume += bids[typeSell][counterSell][v]
            counterSell += 1
            counterBuy += 1

        deals.append((tempBuyNum, tempSellNum, tempVolume))

        if maxValue <= currentVolume * currentPrice:      ### проверяем, увеличился ли объем аукциона в деньгах
            maxValue = currentVolume * currentPrice       ### запоминаем максимальный объем,
            maxValueNum = len(deals)                    ### количество оптимальных сделок
            optPrice = currentPrice                     ### и оптимальную цену

        if marketBuy and counterBuy == len(bids[bm]):   ### если рыночные заявки кончились, переходим на лимитные
            counterBuy = 0
            marketBuy = False

        if marketSell and counterSell == len(bids[sm]):
            counterSell = 0
            marketSell = False

        if (not marketBuy and counterBuy == len(bids[bl])) or (not marketSell and counterSell == len(bids[sl])): ### если ВСЕ заявки закончились, останавливаемся
            break

    return (optPrice, maxValue, maxValueNum)


def write_to_file(result):
    with open('Код МОЕХ-разработка-Зимин Степан Михайлович.csv', 'w') as file:
        write = csv.writer(file, delimiter = ';')
        write.writerow(('OK', result[0], result[1]))
        write.writerows((oneDeal[0], oneDeal[1], oneDeal[2], oneDeal[2]*result[0]) for oneDeal in deals[0:result[2]])