ENDPOINTS = {
  "loopback": {
    "main": {
      "method": "GET",
      "path": "/loopback",
      "summary": "test api",
      "description": "Responds with a static HotelsResponse after 100 ms.",
      "path_params": [],
      "required_params": [],
      "optional_params": [],
      "has_body": False
    }
  },
  "static": {
    "main": {
      "method": "GET",
      "path": "/static",
      "summary": "static data",
      "description": "Delivers all static data needed to pre-fill a search mask.",
      "path_params": [],
      "required_params": [],
      "optional_params": [
        "adults",
        "productType",
        "optionSuperRegionList",
        "optionLocationList",
        "optionSustainable",
        "departureAirportCountryList"
      ],
      "has_body": False
    },
    "regions": {
      "method": "GET",
      "path": "/static/regions",
      "summary": "all regions",
      "description": "Delivers region codes and names including their top regions and countries.",
      "path_params": [],
      "required_params": [],
      "optional_params": [],
      "has_body": False
    },
    "regions_by_id": {
      "method": "GET",
      "path": "/static/regions/{id}",
      "summary": "one region",
      "description": "Delivers one region including its top regions and country.",
      "path_params": [
        "id"
      ],
      "required_params": [
        "id"
      ],
      "optional_params": [],
      "has_body": False
    },
    "airports": {
      "method": "GET",
      "path": "/static/airports",
      "summary": "all airports",
      "description": "Delivers airport codes and names including their countries.",
      "path_params": [],
      "required_params": [],
      "optional_params": [],
      "has_body": False
    },
    "locations": {
      "method": "GET",
      "path": "/static/locations",
      "summary": "all locations",
      "description": "Delivers location codes and names including their regions and countries.\nCAUTION: Lots of data!",
      "path_params": [],
      "required_params": [],
      "optional_params": [],
      "has_body": False
    },
    "country": {
      "method": "GET",
      "path": "/static/country",
      "summary": "country data",
      "description": "Delivers static data for a country.",
      "path_params": [],
      "required_params": [
        "airportCode"
      ],
      "optional_params": [],
      "has_body": False
    },
    "schoolHolidays": {
      "method": "GET",
      "path": "/static/schoolHolidays",
      "summary": "school holidays",
      "description": "Delivers school holidays data for a country and year.",
      "path_params": [],
      "required_params": [
        "country"
      ],
      "optional_params": [
        "state",
        "year"
      ],
      "has_body": False
    },
    "trainstations": {
      "method": "GET",
      "path": "/static/trainstations",
      "summary": "trainstation data",
      "description": "Delivers static data for a trainstations.",
      "path_params": [],
      "required_params": [],
      "optional_params": [],
      "has_body": False
    },
    "giatahotels": {
      "method": "GET",
      "path": "/static/giatahotels",
      "summary": "giata hotel data",
      "description": "Delivers static description data for a giataidList.",
      "path_params": [],
      "required_params": [],
      "optional_params": [
        "giataIdList"
      ],
      "has_body": False
    },
    "rooms": {
      "method": "GET",
      "path": "/static/rooms",
      "summary": "get rooms details",
      "description": "Delivers rooms details",
      "path_params": [],
      "required_params": [],
      "optional_params": [],
      "has_body": False
    },
    "boards": {
      "method": "GET",
      "path": "/static/boards",
      "summary": "get boards details",
      "description": "Delivers boards details",
      "path_params": [],
      "required_params": [],
      "optional_params": [],
      "has_body": False
    },
    "facilities": {
      "method": "GET",
      "path": "/static/facilities",
      "summary": "get facilities details",
      "description": "Delivers facilities details",
      "path_params": [],
      "required_params": [],
      "optional_params": [],
      "has_body": False
    },
    "sustainable": {
      "method": "GET",
      "path": "/static/sustainable",
      "summary": "get sustainable certificates",
      "description": "delivers sustainable information like certificates",
      "path_params": [],
      "required_params": [],
      "optional_params": [],
      "has_body": False
    },
    "cachedetails": {
      "method": "GET",
      "path": "/static/cachedetails",
      "summary": "get cache details",
      "description": "Delivers cache details about hotels. Either hotelCode or giataId is required.",
      "path_params": [],
      "required_params": [
        "tourOperatorList"
      ],
      "optional_params": [
        "tourOperatorCode",
        "hotelCode",
        "giataId",
        "productType"
      ],
      "has_body": False
    },
    "cachedata": {
      "method": "GET",
      "path": "/static/cachedata",
      "summary": "get cache data",
      "description": "Delivers cache data",
      "path_params": [],
      "required_params": [
        "tourOperatorList"
      ],
      "optional_params": [
        "productType",
        "offlineOnly"
      ],
      "has_body": False
    }
  },
  "tourOperators": {
    "main": {
      "method": "GET",
      "path": "/tourOperators",
      "summary": "tour operators",
      "description": "all tour operators",
      "path_params": [],
      "required_params": [],
      "optional_params": [
        "optionActivated"
      ],
      "has_body": False
    },
    "selected": {
      "method": "GET",
      "path": "/tourOperators/selected",
      "summary": "in backend selected tour operators",
      "description": "selected tour operators",
      "path_params": [],
      "required_params": [],
      "optional_params": [],
      "has_body": False
    }
  },
  "completions": {
    "main": {
      "method": "GET",
      "path": "/completions",
      "summary": "auto completion",
      "description": "Serves auto completion of user inputs. Provides several lists of corresponding search results according to chosen options.",
      "path_params": [],
      "required_params": [
        "searchValue"
      ],
      "optional_params": [
        "language",
        "nofuzziness",
        "distributionOnlineOnly",
        "productType",
        "subTypeRegion",
        "subTypeLocation",
        "subTypeHotelChain",
        "subTypeGiataHotel",
        "subTypeDestinationAirport",
        "subTypeCountry",
        "subTypeTrainStation",
        "limit",
        "tourOperatorList",
        "airportList",
        "roomTypeList"
      ],
      "has_body": False
    }
  },
  "regions": {
    "main": {
      "method": "GET",
      "path": "/regions",
      "summary": "available regions",
      "description": "Provides a structured list of (super) regions and their (sub) regions that include available offers for the search. The best prices per region, air and water temperature for the travel date as well as",
      "path_params": [],
      "required_params": [
        "productType",
        "adults"
      ],
      "optional_params": [
        "productSubType",
        "travelType",
        "searchDate",
        "fromDate",
        "toDate",
        "duration",
        "minDuration",
        "maxDuration",
        "strictDate",
        "fromTime",
        "toTime",
        "minDepartureTime",
        "maxDepartureTime",
        "minReturnTime",
        "maxReturnTime"
      ],
      "has_body": False
    }
  },
  "hotels": {
    "main": {
      "method": "GET",
      "path": "/hotels",
      "summary": "search for hotels",
      "description": "Provides a list of hotels having available offers for the search. From-prices per person and for all travellers are given for each hotel. Furthermore, the best offers for accommodation-board combinati",
      "path_params": [],
      "required_params": [
        "productType",
        "adults"
      ],
      "optional_params": [
        "productSubType",
        "travelType",
        "searchDate",
        "fromDate",
        "toDate",
        "duration",
        "minDuration",
        "maxDuration",
        "strictDate",
        "fromTime",
        "toTime",
        "minDepartureTime",
        "maxDepartureTime",
        "minReturnTime",
        "maxReturnTime"
      ],
      "has_body": False
    },
    "top": {
      "method": "GET",
      "path": "/hotels/top",
      "summary": "top hotels per region",
      "description": "Provides a list of top hotels per region",
      "path_params": [],
      "required_params": [
        "productType",
        "adults"
      ],
      "optional_params": [
        "searchDate",
        "fromDate",
        "toDate",
        "duration",
        "minDuration",
        "maxDuration",
        "strictDate",
        "fromTime",
        "toTime",
        "minDepartureTime",
        "maxDepartureTime",
        "minReturnTime",
        "maxReturnTime",
        "children",
        "navigation"
      ],
      "has_body": False
    },
    "get_by_id": {
      "method": "GET",
      "path": "/hotels/{giataId}",
      "summary": "Retrieves non-bookable content for a hotel.",
      "description": "The endpoint returns static or informational pages (e.g., hotel descriptions, FAQs, policy documents) that are not tied to a reservation.",
      "path_params": [
        "giataId"
      ],
      "required_params": [
        "giataId"
      ],
      "optional_params": [
        "tourOperatorList",
        "catalogId",
        "catalogDate",
        "rating[source]",
        "extra[seller]",
        "language",
        "duration"
      ],
      "has_body": False
    },
    "nonBookableContent": {
      "method": "POST",
      "path": "/hotels/nonBookableContent",
      "summary": "Retrieves non-bookable content for hotels.",
      "description": "The endpoint returns static or informational pages (e.g., hotel descriptions, FAQs, policy documents) that are not tied to a reservation. <br><br> **Note:** The giataIdList can be provided either in t",
      "path_params": [],
      "required_params": [],
      "optional_params": [
        "giataIdList",
        "extra[seller]",
        "language"
      ],
      "has_body": True
    },
    "reviews": {
      "method": "GET",
      "path": "/hotels/{giataId}/reviews",
      "summary": "hotel reviews",
      "description": "Hotel reviews",
      "path_params": [
        "giataId"
      ],
      "required_params": [
        "giataId"
      ],
      "optional_params": [
        "source",
        "limit"
      ],
      "has_body": False
    },
    "reviews_2": {
      "method": "POST",
      "path": "/hotels/{giataId}/reviews",
      "summary": "create a hotel review",
      "description": "This request creates a new hotel review.",
      "path_params": [
        "giataId"
      ],
      "required_params": [
        "giataId"
      ],
      "optional_params": [],
      "has_body": True
    },
    "matrix": {
      "method": "GET",
      "path": "/hotels/{giataId}/matrix",
      "summary": "hotel offers matrix",
      "description": "Provides a matrix of all available combinations of room, board and includes services (e.g. transfer) for the selected hotel.",
      "path_params": [
        "giataId"
      ],
      "required_params": [
        "giataId",
        "productType",
        "searchDate",
        "adults"
      ],
      "optional_params": [
        "fromDate",
        "toDate",
        "children"
      ],
      "has_body": False
    },
    "calendar": {
      "method": "GET",
      "path": "/hotels/{giataId}/calendar",
      "summary": "price calendar",
      "description": "provides best price per departure date for a given travel duration",
      "path_params": [
        "giataId"
      ],
      "required_params": [
        "giataId",
        "productType",
        "adults"
      ],
      "optional_params": [
        "searchDate",
        "fromDate",
        "toDate",
        "duration",
        "minDuration",
        "maxDuration",
        "strictDate",
        "fromTime",
        "toTime",
        "minDepartureTime",
        "maxDepartureTime",
        "minReturnTime",
        "maxReturnTime",
        "children",
        "roomTypeList"
      ],
      "has_body": False
    },
    "multiCalendar": {
      "method": "GET",
      "path": "/hotels/{giataId}/multiCalendar",
      "summary": "multi price calendar",
      "description": "provides best price per departure date for all available travel durations<br> a travel duration given in searchDate will be ignored",
      "path_params": [
        "giataId"
      ],
      "required_params": [
        "giataId",
        "productType",
        "adults"
      ],
      "optional_params": [
        "searchDate",
        "fromDate",
        "toDate",
        "duration",
        "minDuration",
        "maxDuration",
        "strictDate",
        "fromTime",
        "toTime",
        "minDepartureTime",
        "maxDepartureTime",
        "minReturnTime",
        "maxReturnTime",
        "children",
        "roomTypeList"
      ],
      "has_body": False
    },
    "priceCalendar": {
      "method": "GET",
      "path": "/hotels/{giataId}/priceCalendar",
      "summary": "extended price calendar",
      "description": "provides best price per date for all available rooms, boards and durations, either on daily or monthly basis<br> will replace both /hotels/{giataId}/calendar and /hotels/{giataId}/multiCalendar in fut",
      "path_params": [
        "giataId"
      ],
      "required_params": [
        "giataId",
        "searchDate",
        "productType",
        "adults"
      ],
      "optional_params": [
        "fromDate",
        "toDate",
        "duration",
        "children",
        "timeInterval",
        "roomTypeList",
        "roomIdList",
        "boardTypeList",
        "tourOperatorList",
        "hotelCodeList",
        "productSubType",
        "travelType",
        "departureAirportList",
        "arrivalAirportList",
        "arrivalAirportListExcluded"
      ],
      "has_body": False
    },
    "recommendations": {
      "method": "GET",
      "path": "/hotels/{giataId}/recommendations",
      "summary": "hotel recommendations related to the hotel identified by {giataId}",
      "description": "Returns a list of hotel recommendations related to the hotel identified by {giataId}.\nRecommendations are generated based on similarity and other factors (e.g., location, category, and guest ratings).",
      "path_params": [
        "giataId"
      ],
      "required_params": [
        "giataId",
        "adults"
      ],
      "optional_params": [
        "productType",
        "children",
        "decorate",
        "records"
      ],
      "has_body": False
    },
    "recommendations_2": {
      "method": "PATCH",
      "path": "/hotels/{giataId}/recommendations",
      "summary": "accept recommended hotel",
      "description": "increases the counter for a recommended hotel (giataId)",
      "path_params": [
        "giataId"
      ],
      "required_params": [
        "giataId"
      ],
      "optional_params": [],
      "has_body": True
    },
    "recommendationFeedback": {
      "method": "POST",
      "path": "/hotels/{giataId}/recommendationFeedback",
      "summary": "accept recommended hotel",
      "description": "to be added",
      "path_params": [
        "giataId"
      ],
      "required_params": [
        "giataId"
      ],
      "optional_params": [],
      "has_body": True
    }
  },
  "offers": {
    "main": {
      "method": "GET",
      "path": "/offers",
      "summary": "search for offers",
      "description": "Provides a list of offers according to search parameters. A CommonOffer element contains the code for identification. Depending on productType a Flight Offer and/or a Hotel Offer and/or a Service Offe",
      "path_params": [],
      "required_params": [
        "productType",
        "adults"
      ],
      "optional_params": [
        "productSubType",
        "travelType",
        "searchDate",
        "fromDate",
        "toDate",
        "duration",
        "minDuration",
        "maxDuration",
        "strictDate",
        "fromTime",
        "toTime",
        "minDepartureTime",
        "maxDepartureTime",
        "minReturnTime",
        "maxReturnTime"
      ],
      "has_body": False
    },
    "pauschal": {
      "method": "GET",
      "path": "/offers/pauschal",
      "summary": "search for pauschal offers",
      "description": "Provides a list of pauschal offers according to the search parameters.",
      "path_params": [],
      "required_params": [
        "adults"
      ],
      "optional_params": [
        "productSubType",
        "searchDate",
        "fromDate",
        "toDate",
        "duration",
        "minDuration",
        "maxDuration",
        "strictDate",
        "fromTime",
        "toTime",
        "minDepartureTime",
        "maxDepartureTime",
        "minReturnTime",
        "maxReturnTime",
        "children"
      ],
      "has_body": False
    },
    "hotelonly": {
      "method": "GET",
      "path": "/offers/hotelonly",
      "summary": "search for hotelonly offers",
      "description": "delivers a list of hotelonly offers according to the search parameters.",
      "path_params": [],
      "required_params": [
        "adults"
      ],
      "optional_params": [
        "searchDate",
        "fromDate",
        "toDate",
        "duration",
        "minDuration",
        "maxDuration",
        "strictDate",
        "fromTime",
        "toTime",
        "minDepartureTime",
        "maxDepartureTime",
        "minReturnTime",
        "maxReturnTime",
        "children",
        "navigation"
      ],
      "has_body": False
    },
    "livehotels": {
      "method": "GET",
      "path": "/offers/livehotels",
      "summary": "search for live offers in Expedia",
      "description": "delivers a list of live offers from Expedia according to the search parameters.",
      "path_params": [],
      "required_params": [
        "adults",
        "tourOperatorList"
      ],
      "optional_params": [
        "searchDate",
        "fromDate",
        "toDate",
        "duration",
        "minDuration",
        "maxDuration",
        "strictDate",
        "fromTime",
        "toTime",
        "minDepartureTime",
        "maxDepartureTime",
        "minReturnTime",
        "maxReturnTime",
        "children",
        "navigation"
      ],
      "has_body": False
    },
    "railtravel": {
      "method": "GET",
      "path": "/offers/railtravel",
      "summary": "search for railtravel offers",
      "description": "Provides a list of railtravel offers according to the search parameters.",
      "path_params": [],
      "required_params": [
        "adults"
      ],
      "optional_params": [
        "searchDate",
        "fromDate",
        "toDate",
        "duration",
        "minDuration",
        "maxDuration",
        "strictDate",
        "fromTime",
        "toTime",
        "minDepartureTime",
        "maxDepartureTime",
        "minReturnTime",
        "maxReturnTime",
        "children",
        "navigation"
      ],
      "has_body": False
    },
    "flight": {
      "method": "GET",
      "path": "/offers/flight",
      "summary": "search for return flight offers",
      "description": "Provides a list of flight offers according to the search parameters.",
      "path_params": [],
      "required_params": [
        "adults"
      ],
      "optional_params": [
        "searchDate",
        "fromDate",
        "toDate",
        "duration",
        "minDuration",
        "maxDuration",
        "strictDate",
        "fromTime",
        "toTime",
        "minDepartureTime",
        "maxDepartureTime",
        "minReturnTime",
        "maxReturnTime",
        "children",
        "navigation"
      ],
      "has_body": False
    },
    "oneway": {
      "method": "GET",
      "path": "/offers/oneway",
      "summary": "search for oneway flight offers",
      "description": "Provides a list of oneway offers according to the search parameters.",
      "path_params": [],
      "required_params": [
        "searchDate",
        "adults"
      ],
      "optional_params": [
        "fromDate",
        "toDate",
        "duration",
        "children",
        "navigation",
        "departureAirportList",
        "arrivalAirportList",
        "flight[carrierCodeList]",
        "flight[flightNumber]",
        "flight[bookingClass]",
        "flight[directness]",
        "flight[stopover]",
        "flight[tariff]",
        "flight[travelClass]",
        "flight[knownLegsOnly]"
      ],
      "has_body": False
    },
    "multicity": {
      "method": "GET",
      "path": "/offers/multicity",
      "summary": "dynamic packaging search for related oneway flights and hotel offers",
      "description": "Provides two common offer lists each for flight offers and for hotel offers according to the search parameters.",
      "path_params": [],
      "required_params": [
        "searchDate",
        "adults",
        "departureAirportList",
        "arrivalAirportList"
      ],
      "optional_params": [
        "fromDate",
        "toDate",
        "duration",
        "children",
        "navigation",
        "countryList",
        "regionList",
        "locationList",
        "giataIdList",
        "tourOperatorList",
        "hotelCodeList",
        "roomTypeList",
        "boardTypeList",
        "keywordList",
        "transferList"
      ],
      "has_body": False
    },
    "multicity_flights": {
      "method": "GET",
      "path": "/offers/multicity/flights",
      "summary": "dynamic search for oneway flights",
      "description": "Provides a common offer list for flight offers according to the search parameters.",
      "path_params": [],
      "required_params": [
        "searchDate",
        "adults",
        "departureAirportList",
        "arrivalAirportList"
      ],
      "optional_params": [
        "fromDate",
        "toDate",
        "children",
        "navigation",
        "tourOperatorList",
        "minPricePerPerson",
        "maxPricePerPerson",
        "minTotalPrice",
        "maxTotalPrice",
        "sortBy",
        "sortDir"
      ],
      "has_body": False
    },
    "multicity_hotels": {
      "method": "GET",
      "path": "/offers/multicity/hotels",
      "summary": "dynamic search for hotel offers",
      "description": "Provides a common offer list for hotel offers according to the search parameters.",
      "path_params": [],
      "required_params": [
        "searchDate",
        "adults"
      ],
      "optional_params": [
        "fromDate",
        "toDate",
        "duration",
        "children",
        "navigation",
        "arrivalAirportList",
        "countryList",
        "regionList",
        "locationList",
        "giataIdList",
        "tourOperatorList",
        "hotelCodeList",
        "roomTypeList",
        "boardTypeList",
        "keywordList"
      ],
      "has_body": False
    },
    "insurance": {
      "method": "GET",
      "path": "/offers/insurance",
      "summary": "search for insurance offers",
      "description": "Provides a list of insurance offers according to the search parameters.",
      "path_params": [],
      "required_params": [
        "arrivalAirportList",
        "tourOperatorList",
        "offerTotalPrice"
      ],
      "optional_params": [
        "searchDate",
        "fromDate",
        "toDate",
        "duration",
        "adults",
        "children",
        "travellerList",
        "offerProductType",
        "offerTourOperator",
        "countryCode",
        "giataId"
      ],
      "has_body": False
    },
    "carrent": {
      "method": "GET",
      "path": "/offers/carrent",
      "summary": "search for rental cars",
      "description": "Provides a list of rental car offers.",
      "path_params": [],
      "required_params": [
        "adults",
        "arrivalAirportList",
        "tourOperatorList"
      ],
      "optional_params": [
        "children",
        "searchDate",
        "fromDate",
        "toDate",
        "duration",
        "minDuration",
        "maxDuration",
        "strictDate",
        "fromTime",
        "toTime",
        "minDepartureTime",
        "maxDepartureTime",
        "minReturnTime",
        "maxReturnTime",
        "filters[inc]"
      ],
      "has_body": False
    },
    "carrent_filters": {
      "method": "GET",
      "path": "/offers/carrent/filters",
      "summary": "rental car search filters",
      "description": "Provides a list of filters for rental car offers search.",
      "path_params": [],
      "required_params": [],
      "optional_params": [],
      "has_body": False
    },
    "parking": {
      "method": "GET",
      "path": "/offers/parking",
      "summary": "search for parking facilities",
      "description": "Provides a list of parking offers.",
      "path_params": [],
      "required_params": [
        "adults",
        "searchDate",
        "departureAirportList",
        "tourOperatorList"
      ],
      "optional_params": [
        "children",
        "fromDate",
        "toDate",
        "duration",
        "minDuration",
        "maxDuration",
        "strictDate",
        "fromTime",
        "toTime",
        "minDepartureTime",
        "maxDepartureTime",
        "minReturnTime",
        "maxReturnTime"
      ],
      "has_body": False
    },
    "deals": {
      "method": "GET",
      "path": "/offers/deals",
      "summary": "search for offers which recently became cheaper",
      "description": "Provides a list of offers according to the search parameters.",
      "path_params": [],
      "required_params": [
        "adults"
      ],
      "optional_params": [
        "searchDate",
        "fromDate",
        "toDate",
        "duration",
        "minDuration",
        "maxDuration",
        "strictDate",
        "fromTime",
        "toTime",
        "minDepartureTime",
        "maxDepartureTime",
        "minReturnTime",
        "maxReturnTime",
        "children",
        "hours"
      ],
      "has_body": False
    },
    "priceCalendar": {
      "method": "GET",
      "path": "/offers/priceCalendar",
      "summary": "price calender",
      "description": "provides best price per date for all available rooms, boards and durations, either on daily or monthly basis for multiple hotels",
      "path_params": [],
      "required_params": [
        "searchDate",
        "productType",
        "adults"
      ],
      "optional_params": [
        "fromDate",
        "toDate",
        "duration",
        "children",
        "timeInterval",
        "roomTypeList",
        "roomIdList",
        "boardTypeList",
        "tourOperatorList",
        "hotelCodeList",
        "productSubType",
        "travelType",
        "departureAirportList",
        "arrivalAirportList",
        "arrivalAirportListExcluded"
      ],
      "has_body": False
    },
    "get_by_id": {
      "method": "GET",
      "path": "/offers/{code}",
      "summary": "verify an offer",
      "description": "Verifies an offer, i.e. checks price and availability at tour operator's backend.",
      "path_params": [
        "code"
      ],
      "required_params": [
        "code",
        "adults"
      ],
      "optional_params": [
        "children",
        "travellerList",
        "type",
        "optionAlternativeFlightOfferList",
        "alternativeFlightPaging[outboundPrevious]",
        "alternativeFlightPaging[inboundPrevious]",
        "alternativeFlightPaging[outboundNext]",
        "alternativeFlightPaging[inboundNext]",
        "addonList",
        "restrictionList",
        "timeout",
        "language",
        "cancellationPoliciesDetails"
      ],
      "has_body": False
    },
    "addons": {
      "method": "GET",
      "path": "/offers/{code}/addons",
      "summary": "available addons of a given offer",
      "description": "Provides a list of addons to a give offer.",
      "path_params": [
        "code"
      ],
      "required_params": [
        "code",
        "adults"
      ],
      "optional_params": [
        "children",
        "addonType",
        "offerTotalPrice",
        "optionCurrencyFilter",
        "language"
      ],
      "has_body": False
    },
    "payments": {
      "method": "GET",
      "path": "/offers/{code}/payments",
      "summary": "available payments of a given offer",
      "description": "Provides a list of payment offers.",
      "path_params": [
        "code"
      ],
      "required_params": [
        "code",
        "adults"
      ],
      "optional_params": [
        "children",
        "language"
      ],
      "has_body": False
    },
    "alternativeFlights": {
      "method": "GET",
      "path": "/offers/{code}/alternativeFlights",
      "summary": "available alternative flights of a given package offer",
      "description": "Provides a list of offers having alternative flights.\nWorks for certain tour operators only, e.g. VTO, SLRD, TJAX",
      "path_params": [
        "code"
      ],
      "required_params": [
        "code",
        "adults"
      ],
      "optional_params": [
        "children",
        "language"
      ],
      "has_body": False
    }
  },
  "bookings": {
    "main": {
      "method": "GET",
      "path": "/bookings",
      "summary": "list bookings",
      "description": "Provides a list of all bookings made by the given account.",
      "path_params": [],
      "required_params": [],
      "optional_params": [
        "navigation",
        "fromCreatedDateTime",
        "toCreatedDateTime",
        "departureAirportCode",
        "arrivalAirportCode",
        "tourOperatorCode",
        "firstTravellerName",
        "customerName",
        "customerFirstName",
        "customerStreet",
        "customerCity",
        "customerZipCode",
        "customerPhone",
        "bookingProductType",
        "changedDate"
      ],
      "has_body": False
    },
    "main_2": {
      "method": "POST",
      "path": "/bookings",
      "summary": "book an offer",
      "description": "This request creates a new booking.",
      "path_params": [],
      "required_params": [],
      "optional_params": [
        "language"
      ],
      "has_body": True
    },
    "get_by_id": {
      "method": "GET",
      "path": "/bookings/{id}",
      "summary": "booking details",
      "description": "Book details",
      "path_params": [
        "id"
      ],
      "required_params": [
        "id"
      ],
      "optional_params": [
        "language"
      ],
      "has_body": False
    },
    "get_by_id_2": {
      "method": "PATCH",
      "path": "/bookings/{id}",
      "summary": "fixing an option",
      "description": "Fixes an option on the tour operator side.",
      "path_params": [
        "id"
      ],
      "required_params": [
        "id"
      ],
      "optional_params": [
        "language"
      ],
      "has_body": True
    },
    "addons": {
      "method": "GET",
      "path": "/bookings/{id}/addons",
      "summary": "booking addons",
      "description": "Book details",
      "path_params": [
        "id"
      ],
      "required_params": [
        "id"
      ],
      "optional_params": [
        "language"
      ],
      "has_body": False
    }
  },
  "documents": {
    "conditions": {
      "method": "POST",
      "path": "/documents/conditions",
      "summary": "creates a terms and conditions document",
      "description": "This request creates a document and provides filename (body) and location (header).",
      "path_params": [],
      "required_params": [],
      "optional_params": [],
      "has_body": True
    },
    "forms": {
      "method": "POST",
      "path": "/documents/forms",
      "summary": "creates a form document",
      "description": "This request creates a document and provides filename (body) and location (header).",
      "path_params": [],
      "required_params": [],
      "optional_params": [],
      "has_body": True
    },
    "visa": {
      "method": "POST",
      "path": "/documents/visa",
      "summary": "creates a visa and entry requirements document",
      "description": "This request creates a document and provides filename (body) and location (header).",
      "path_params": [],
      "required_params": [],
      "optional_params": [],
      "has_body": True
    },
    "descriptions": {
      "method": "POST",
      "path": "/documents/descriptions",
      "summary": "creates a custom hotel description document",
      "description": "This request creates a pdf document with given text or html and provides filename (body) and location (header).",
      "path_params": [],
      "required_params": [],
      "optional_params": [],
      "has_body": True
    },
    "verifiedOffers": {
      "method": "POST",
      "path": "/documents/verifiedOffers",
      "summary": "creates a json document from a verified offer response",
      "description": "This request creates a json document with given offer verify response or html and provides filename (body) and location (header).",
      "path_params": [],
      "required_params": [],
      "optional_params": [],
      "has_body": True
    },
    "get_by_id": {
      "method": "GET",
      "path": "/documents/{document}",
      "summary": "returns a document",
      "description": "This request returns a document.",
      "path_params": [
        "document"
      ],
      "required_params": [
        "document"
      ],
      "optional_params": [],
      "has_body": False
    }
  },
  "experimental": {
    "matchOffers": {
      "method": "POST",
      "path": "/experimental/matchOffers",
      "summary": "match offers from external sources and traffics",
      "description": "match offers from external sources and traffics",
      "path_params": [],
      "required_params": [],
      "optional_params": [
        "source",
        "priceTolerance"
      ],
      "has_body": True
    }
  }
}