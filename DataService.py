import pandas as pd
import numpy as np

jhu_opt = {"N": 1, "only_contiguous": True, "max_date": "last"}
jhu_global_opt = {"N": 1, "max_date": "last"}
brasil_opt = {"N": 1, "max_date": "last"}


class DataService:
  __instance = None

  @staticmethod
  def getInstance(jhu_options=jhu_opt,
                  jhu_global_options = jhu_global_opt,
                  brasil_options=brasil_opt):
    """Returns instance of DataService.
    This implements a Singleton pattern to make sure that the same instance of this class will be used everywhere
    
    Returns:
        {DataService} -- DataService instance
    """

    if DataService.__instance == None:
      DataService(jhu_options,jhu_global_options, brasil_options)
    return DataService.__instance

  def __init__(self, jhu_options, jhu_global_options, brasil_options):
    """ Virtually private constructor. """
    if DataService.__instance != None:
      raise Exception("This class is a singleton!")
    else:
      self.jhu_data = None
      self.jhu_metadata = dict()
      self.jhu_global_data = None
      self.jhu_global_metadata = dict()
      self.brasil_io_data = None
      self.brasil_io_metadata = dict()
      self.start_date_columns = {"jhu": 5, "jhu_global": 3, "brasil_io": 3}
      self.jhu_options = jhu_options
      self.jhu_global_options = jhu_global_options
      self.brasil_options = brasil_options
      DataService.__instance = self

  def get_jhu_data(self, force=False):
    """Get data from JHU and save locally
    
    Keyword Arguments:
        force {bool} -- If true, get data even if its cached (default: {False})
    
    Returns:
        {DataFrame} -- Data from JHU
    """
    if not self.jhu_data or force:
      jhu_url = "https://raw.githubusercontent.com/CSSEGISandData/"\
          "COVID-19/master/csse_covid_19_data/"\
          "csse_covid_19_time_series/"\
          "time_series_covid19_confirmed_US.csv"

      self.jhu_data = pd.read_csv(jhu_url)
    return self.jhu_data.copy()

  def get_jhu_global_data(self, force=False):
    """Get global data from JHU and save locally
    
    Keyword Arguments:
        force {bool} -- If true, get data even if its cached (default: {False})
    
    Returns:
        {DataFrame} -- Data from JHU
    """
    if not self.jhu_global_data or force:
      jhu_url = "https://raw.githubusercontent.com/CSSEGISandData/"\
          "COVID-19/master/csse_covid_19_data/"\
          "csse_covid_19_time_series/"\
          "time_series_covid19_confirmed_global.csv"

      self.jhu_data = pd.read_csv(jhu_url)
    return self.jhu_data.copy()
      

  def get_brasil_io_data(self, force=False):
    """Get data from brasil.io and save locally
    
    Keyword Arguments:
        force {bool} -- If true, get data even if its cached (default: {False})
    
    Returns:
        {DataFrame} -- Data from brasil.io
    """

    if not self.brasil_io_data or force:
      brasil_io_url = "https://brasil.io/dataset/covid19/caso/?place_type=city&format=csv"

      self.brasil_io_data = pd.read_csv(brasil_io_url)
    return self.brasil_io_data.copy()

  def __filter_N_max_data(self, source, data, N, max_date):
    """Filters DataFrama from source by N and max_date
    
    Arguments:
        source {str} -- Source of data. Either 'jhu', 'jhu_global' or 'brasil_io'
        data {DataFrame} -- DataFrame to filter
        N {int} -- Minimal number of cases
        max_date {str} -- If default, return cases from all dates. If defined, return cases until defined date. Format m/d/yy (default: {"last"})
    
    Returns:
        {DataFrame} -- Filtered DataFrame
    """

    metadata = self.jhu_metadata if source == "jhu" else self.brasil_io_metadata\
        if source =="brasil_io" else self.jhu_global_metadata
    start_date_columns = self.start_date_columns[source]
    metadata["date_cols"] = list(data.columns)

    if max_date == "last":
      metadata["date_cols"] = metadata["date_cols"][start_date_columns:]
    else:
      metadata["date_cols"] = metadata["date_cols"][start_date_columns:data.
                                                    columns.get_loc(max_date)]

    data = data.sort_values(by=metadata["date_cols"],
                            ascending=np.zeros(len(metadata["date_cols"]),
                                               dtype=bool))
    
    nfi = []
    metadata["uid_positive"] = []
    for uid in data['UID'].tolist():
      n_infection = next(
        (i for i, x in enumerate(data.loc[data['UID'] == uid,
                                          metadata["date_cols"]].values[0])
         if x >= N), "None")
      if n_infection != "None":
        metadata["uid_positive"].append(uid)
      nfi.append(n_infection)

    data.insert(start_date_columns, "Day_First_N_Infections", nfi)
    return data

  def get_filtered_brasil_io_data(self, options=None):
    """Get data from Brasil.io and filters it using the arguments on the same format as JHU data
    
    Keyword Arguments:
        options {BrasilOptions} -- Options to be used in the filter
    
    Returns:
        {DataFrame} -- Brasil DataFrame filtered by arguments
    """
    options = options if options != None else self.brasil_options
    N = options["N"]
    max_date = options["max_date"]

    data = self.get_brasil_io_data()
    data = data[data.city != "Importados/Indefinidos"]

    city_names = data["city"].unique().tolist()
    dates = data["date"].unique().tolist()

    ufs = []
    uids = []
    for city in city_names:
      ufs.append(data.loc[data["city"] == city, "state"].values[0])
      uids.append(data.loc[data["city"] == city, "city_ibge_code"].values[0])

    # Usa o mesmo nome de colunas do arquivo da JHU por simplicidade
    new_data = pd.DataFrame(data=uids, columns=["UID"])

    new_data["city"] = city_names
    new_data["Province_State"] = ufs

    for date in dates:
      daily_data = data.loc[data["date"] == date]
      codes = daily_data["city_ibge_code"].tolist()
      new_data[date] = np.zeros(len(uids))

      for code in codes:
        if code in uids:
          i = new_data.index[new_data["UID"] == code].values[0]
          new_data.at[i, date] = daily_data.loc[daily_data["city_ibge_code"] ==
                                                code, "confirmed"].values[0]

    return self.__filter_N_max_data('brasil_io', new_data, N, max_date)

  def get_filtered_jhu_data(self, options=None):
    """Get data from JHU and filters it using the arguments
    
       Keyword Arguments:
         options {JhuOptions} Options to be used in the filter
    
       Returns:
        {DataFrame} -- JHU DataFrame filtered by arguments
    """
    options = options if options != None else self.jhu_options
    N = options["N"]
    only_contiguous = options["only_contiguous"]
    max_date = options["max_date"]

    non_contiguous = [
      "American Samoa", "Guam", "Northern Mariana Islands", "Puerto Rico",
      "Virgin Islands", "Hawaii", "Alaska"
    ]

    data = self.get_jhu_data()
    data = data.drop(columns=['iso2', 'iso3', 'code3', 'FIPS', 'Lat', 'Long_'])
    if only_contiguous:
      data = data.loc[~data['Province_State'].isin(non_contiguous)]

    return self.__filter_N_max_data('jhu', data, N, max_date)

  def get_clustered_global_jhu_data(self, options=None):
      """Get data from JHU and groups by country
    
         Returns:
          {DataFrame} -- JHU global DataFrame by country
      """
      options = options if options != None else self.jhu_global_options
      N = options["N"]
      max_date = options["max_date"]
      
      data = self.get_jhu_global_data()
      data = data.groupby(['Country/Region']).sum()
      data = data.reset_index()
      data = data.rename(columns={'Country/Region': 'UID'})
      
      self.jhu_global_data = data
      
      return self.__filter_N_max_data('jhu_global', data, N, max_date)

  def save_to_file(self, data, out_file="output.csv"):
    """Save DataFrame to csv file
    
    Arguments:
        data {DataFrame} -- DataFrame to be save as a csv file
    
    Keyword Arguments:
        out_file {str} -- Output file name (default: {"output.csv"})
    """

    data.to_csv(out_file)
