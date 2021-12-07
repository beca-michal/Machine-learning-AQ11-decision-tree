import pandas as pd
import numpy as np

# upravi data aby sa neopakovali a vrati 2 vystupy: 
# trenovaciu mnozinu ktora ma urcenu triedu
# testovaciu mnozinu (riadky ktorym chyba trieda, teda riadky s prazdnym poslednym stlpcom)
#def correct_repeated_data(data):
#    unpredicted = pd.DataFrame(columns=data.columns)
#    for row in range(0, data.shape[0]):
#        for idx, item in enumerate(data.iloc[row,:-1]):
#            change = str(data.iloc[row,idx]) + "({})".format(data.columns[idx])
#            data.iloc[row,idx] = change
#        if pd.isna(data.iloc[row,-1]):
#            unpredicted.loc[len(unpredicted.index)] = data.iloc[row,:]
#            data.drop(row, axis=0)
#    #print(unpredicted)
#    data = data.dropna(how='any',axis=0)
#    return data, unpredicted

def absorbcia(envelope_row):
    tmp = envelope_row.copy()
    for idx,obalka in enumerate(envelope_row):
        for x in range(idx,len(envelope_row)):
            #print(idx, obalka, x)
            if idx != x:
                if (set(obalka).issubset(set(envelope_row[x]))):
                    #print("removed:", x, envelope_row[x])
                    if envelope_row[x] in tmp:
                        tmp.remove(envelope_row[x])
                    #print("New tmp",tmp)
                    #print("envelope", envelope_row)
    return tmp

def absorb_final_flatten(absorb):
    flatten_first = list()
    for env in absorb:
        if len(env) > 1:
            for idx, zatvorka in enumerate(env[:-1]):
                if len(env[idx+1]) > 1:
                    for string in env[idx+1]:
                        item = zatvorka.copy()
                        item.append(string)
                        flatten_first.append(item)
                else:
                    flatten_first += [env[idx] + env[idx+1]]
        else:
            flatten_first += list(env)

    result = absorbcia(flatten_first)
    #print("Pred absorb", flatten_first)
    #print("Po absorb", result)
    return result

def envelopes(data):
    header = list(data.columns[:-1]) #názvy stĺpcov bez tried
    data = np.array(data)
    classes_rows_indexes = dict()
    envelopes = dict() #tu budeme ukladať čiastkové výsledky pre kontrolu
    unique, counts = np.unique(data[:,-1], return_counts = True)
    classes_count = dict(zip(unique, counts)) #pocet pripadov(riadkov) kazdej triedy
    print("Počet výsledkov jednotlivých tried:\n",classes_count)

    #definujeme prazdny dict
    for i in range(0, len(unique)):
        classes_rows_indexes.update({unique[i]: list()})

    #classes_rows_indexes je dict s indexami riadkov danej triedy
    for row in range(0, data.shape[0]):
        classes_rows_indexes[data[row,-1]].append(row)
    print("Indexy riadkov jednotlivých tried:\n",classes_rows_indexes)

#______________________________________________________________________________________________
    print("\nOBÁLKY G(+)/(-):")
    absorb_first = list() #Tu budú uložené obálky po zákone absorbcie
    for row_positive in list(classes_rows_indexes.values())[0]: #prechadzame riadkami (+) triedy
        envelope_row = list() #
        for row_negative in list(classes_rows_indexes.values())[1]: #prechadzame riadkami (-) triedy
            specific_envelope = list() #stĺpce (najmenšie obálky - neskôr spájame)
            for col in range(0, data.shape[1]-1): #prechadzame stlpcami col
                if data[row_positive,col] != data[row_negative,col]: #Porovnávame pozitívny riadok s negatívnym pre konkrétny stĺpec
                    specific_envelope.append("{}#{}".format(header[col], data[row_negative,col]))
            print("G({}/{}): {}".format(row_positive, row_negative, specific_envelope))
            if specific_envelope is not None:
                envelopes.update({"G{}/{}".format(row_positive, row_negative): specific_envelope}) #pomocny list envelopes ukladame tu čiastkové výsledky
                if specific_envelope not in envelope_row:
                    envelope_row.append(specific_envelope) #spájame všetky obálky a opakujúce sa vyhodíme
            else:
                print("G{}/{} not have envelope".format(row_positive, row_negative))

        envelope_row.sort(key=len)
        print("G({}/({})): {}".format(row_positive, unique[1], envelope_row))

        reduc_first = absorbcia(envelope_row)
        print("Zakon absorbcie: G({}/({})): {}\n".format(row_positive, unique[1], reduc_first))

        if reduc_first not in absorb_first:
            absorb_first.append(reduc_first)
            
#______________________________________________________________________________________________
    print("\nOBÁLKY G(-)/(+):")
    absorb_sec = list() #Tu budú uložené obálky po zákone absorbcie opačne
    for row_negative in list(classes_rows_indexes.values())[1]: #prechadzame riadkami (-) triedy
        envelope_row = list() #
        for row_positive in list(classes_rows_indexes.values())[0]: #prechadzame riadkami (+) triedy
            specific_envelope = list() #stĺpce (najmenšie obálky - neskôr spájame)
            for col in range(0, data.shape[1]-1): #prechadzame stlpcami col
                if data[row_positive,col] != data[row_negative,col]: #Porovnávame negatívny riadok s pozitívnym pre konkrétny stĺpec
                    specific_envelope.append("{}#{}".format(header[col], data[row_positive,col]))
            print("G({}/{}): {}".format(row_negative, row_positive, specific_envelope))
            if specific_envelope is not None:
                envelopes.update({"G{}/{}".format(row_negative, row_positive): specific_envelope}) #pomocny list envelopes ukladame tu čiastkové výsledky
                if specific_envelope not in envelope_row:
                    envelope_row.append(specific_envelope)  #spájame všetky obálky a opakujúce sa vyhodíme
            else:
                print("G{}/{} not have envelope".format(row_negative, row_positive))

        envelope_row.sort(key=len)
        print("G({}/({})): {}".format(row_negative, unique[0], envelope_row))  #všetky jedinečné obálky pohromade

        reduc_sec = absorbcia(envelope_row) #absorbcia

        print("Zakon absorbcie: G(({})/{}): {}\n".format(unique[0], row_negative, reduc_sec))

        if reduc_sec not in absorb_sec:
            absorb_sec.append(reduc_sec) #spájame všetky absorbcie jednotlivých riadkov

#______________________________________________________________________________________________
    #Upravime tak, že spravíme flatten od list of lists (lebo sme mali veľmi vnorené listy do seba) a spravime absorbciu výsledných obálok pre obe triedy

    #Finálna absorbcia +/-
    result_one = absorb_final_flatten(absorb_first)
    result_two = absorb_final_flatten(absorb_sec)

    print("Vysledok pred Absrobciou:")
    print("G(({})/({})): {}".format(unique[0], unique[1], absorb_first))
    print("Absorbcia:")
    print("G(({})/({})): {}".format(unique[0], unique[1], result_one))

    print("\nVysledok pred Absrobciou:")
    print("G(({})/({})): {}".format(unique[1], unique[0], absorb_sec))
    print("Absorbcia:")
    print("G(({})/({})): {}".format(unique[1], unique[0], result_two))
    #print(envelopes)


#cviko_data = pd.read_csv('cviko.csv',delimiter=';')
cviko_data = pd.read_csv('cviko.csv',delimiter=';')
print(cviko_data)
#data, unpredicted = correct_repeated_data(cviko_data)
#print(data)
#print(unpredicted)
envelopes(cviko_data)




