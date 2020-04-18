# -*- coding: utf-8 -*-
"""
Created on Sat Apr 18 14:41:44 2020

"""
import pandas as pd
import numpy as np
import urllib as ul
import gzip
import matplotlib.pyplot as mp

class TimeSeries:
    __NON_CONTIGUOUS_US = [
        "American Samoa", "Guam", "Northern Mariana Islands",\
        "Puerto Rico", "Virgin Islands", "Hawaii", "Alaska"]

    __JHU = "https://raw.githubusercontent.com/CSSEGISandData/"\
        "COVID-19/master/csse_covid_19_data/"\
        "csse_covid_19_time_series/"\
        "time_series_covid19_confirmed_US.csv"

    __BR_IO = "https://data.brasil.io/dataset/covid19/caso_full.csv.gz"

    def __init__(
            self, N, territory, raw_data="standard", only_contiguous=True,
            max_date="last"):
        """ Trata a serie temporal de casos por unidade territorial (condados ou municipios).

        Parameters
        ----------
        N : inteiro positivo
            Numero de casos inicial minimo
        territory: string
            Indica a origem do arquivo, ou filtros a serem aplicados ao dataset
            de acordo com a necessidade
        raw_data : string (url ou path), optional
            Se nao definido, usa o respositorio online da JHU
        only_contiguous : booleano, optional
            Se falso, considera os territorios nao continentais dos EUA, e o
            Alaska
        max_date : string (data formato americano - m/d/aa), opcional
            Se padrao, recupera ate a ultima data do arquivo. Se definido,
            recupera os dados ate a data informada

        Returns
        -------
        None.

        """
        self.territory = territory
        self.N = N

        if (raw_data == "standard"):
            self.get_online_dataset(territory)
        else:
            self.raw_data = raw_data

        if territory == "US":
           # Remove colunas nao usadas
           self.data = pd.read_csv(self.raw_data)\
               .drop(columns=['iso2', 'iso3', 'code3', 'FIPS', 'Lat', 'Long_'])

           if only_contiguous:
              self.data = self.data.loc[
                  ~self.data['Province_State'].isin(self.__NON_CONTIGUOUS_US)]

           startdate_cols = 5
           self.out_file_name = "_counties_diff_US.csv"
        if territory == "BR":
            self.data = pd.read_csv(self.raw_data)
            startdate_cols = 3
            self.out_file_name = "_municipios_dif_BR.csv"

        # Colunas temporais
        self.date_cols = list(self.data.columns)
        if max_date == "last":
            self.date_cols = self.date_cols[startdate_cols:]
        else:
            self.date_cols = self.date_cols[
                startdate_cols:self.data.columns.get_loc(max_date)]

        # Remove os totais de casos menores que N para a ordenacao
        num_data = self.data._get_numeric_data()
        num_data[num_data < N] = 0

        # Ordena conforme os primeiros casos aparecem
        self.data = self.data.sort_values(by=self.date_cols,
                            ascending=np.zeros(
                                len(self.date_cols), dtype=bool))

        # Encontra o primeiro dia em que o condado atinge N casos
        # e remove da analise os condados sem casos confirmados
        nfi = []
        self.uid_positive = []
        for uid in list(x for x in self.data['UID']):
            n_infection = next((i for i, x in enumerate(
                self.data.loc[
                    self.data['UID'] == uid,
                    self.date_cols].values[0]) if x >= N), "None")
            if n_infection != "None":
                self.uid_positive.append(uid)
            nfi.append(n_infection)

        self.data.insert(self.startdate_cols, "Day_First_N_Infections", nfi)

    def save_data_file(self, path=""):
        """ Salva os dados com a coluna de dias ate a infeccao N apos outbreak
        """
        self.data.to_csv(
            path +
            "time_series_" +
            str(self.N) + "_" +
            self.territory + "_" +
            self.date_cols[-1] + "_"
            ".csv", index=False)

    def get_online_dataset(self, territory):
        """ Recupera os arquivos atualizados para um dado territorio
        """
        if territory == "US":
            url = self.__JHU
        elif territory == "BR":
            url = self.__BR_IO

        file = "data/" + url.split("/")[-1]
        ul.request(url, file)
        if ".gz" in url:
            file_csv = open(file.replace(".gz", ""), "wb")
            with gzip.open(file, "rb") as fgz:
                content = fgz.read()
            file_csv.write(content)
            file_csv.close()
        
        if territory == "BR":
            data = self._gen_table_br(file)
            file = "data/time_series_covid19_confirmed_BR.csv"
            data.to_csv(file)

        self.raw_data = file

    def hist_first_infections(self, out_file, x_label, title, divs=45):
        """ Salva um histograma da distribuicao de primeiros N casos desde outbreak
        """
        fig, plot = mp.subplots(
            1, 1, figsize=(10, 10), constrained_layout=True)

        filtered_data = self.data[self.data.Day_First_N_Infections != "None"]
        plot.hist(filtered_data["Day_First_N_Infections"].values, bins=divs)
        mp.xlabel(x_label, fontsize=18)
        mp.ylabel("Frequency", fontsize=18)
        mp.title(title, fontsize=22)
        fig.savefig(out_file)
        
    def _gen_table_br(self, raw):
        """Gera uma tabela JHU-like para a serie temporal de casos de covid-19 no Brasil.

        Parameters
        ----------
        raw : string, optional
            Caminho para o arquivo original. The default is "caso_full.csv".
            
        Returns
        -------
        None. Salva um arquivo em disco com a serie temporal.

        """
        io_data = pd.read_csv(raw)

        io_data = io_data[io_data.city != "Importados/Indefinidos"]

        cities_codes = io_data["city_ibge_code"].unique().tolist()
        dates = io_data["date"].unique().tolist()

        # Usa o mesmo nome de colunas do arquivo da JHU por simplicidade
        new_data = pd.DataFrame(data=cities_codes, columns=["UID"])

        cities_names = []
        ufs = []
        for cco in cities_codes:
            name = io_data.loc[io_data["city_ibge_code"] == cco, "city"].values[0]
            state = io_data.loc[io_data["city_ibge_code"] == cco, "state"].values[0]
            cities_names.append(name)
            ufs.append(state)

        new_data["city"] = cities_names
        new_data["Province_State"] = ufs

        for date in dates:
            daily_data = io_data.loc[io_data["date"] == date]
            codes = daily_data["city_ibge_code"].tolist()
            new_data[date] = np.zeros(len(cities_codes))

            for code in codes:
                i = new_data.index[new_data["UID"] == code].values[0]
                new_data.at[i, date] = daily_data.loc[
                    daily_data["city_ibge_code"] == code,
                    "last_available_confirmed"].values[0]
        
        return(new_data)
        new_data.to_csv("time_series_confirmed_BR.csv", index=False)