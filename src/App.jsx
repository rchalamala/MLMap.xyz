import { Fragment, useState, useEffect, useRef } from "react";
import { CheckIcon, ChevronUpDownIcon } from "@heroicons/react/20/solid";
import getData from "./getData";
import getPaper from "./getPaper";
import { postSearch } from "./postSearch";
import { postAbstract } from "./postAbstract";
import {
  conferences,
  years,
  default as EmbeddingVisualization,
} from "./EmbeddingVisualization";
import AbstractForm from "./AbstractForm";
import InstructionPopup from "./InstructionPopup";

import { Listbox, Transition } from "@headlessui/react";

function CustomListbox({
  value,
  onChange,
  options,
  label,
  displayValueName,
  className,
}) {
  return (
    <Listbox value={value} onChange={onChange} multiple className={className}>
      <div className="relative">
        <Listbox.Button className="relative max-h-40 w-full cursor-default rounded-lg bg-white py-2 pl-3 pr-10 text-left text-sm hover:cursor-pointer focus:outline-none focus-visible:border-sky-500 focus-visible:ring-2 focus-visible:ring-white focus-visible:ring-opacity-75 focus-visible:ring-offset-2 focus-visible:ring-offset-sky-300">
          <span className="block truncate">
            {Object.keys(value).length !== Object.keys(options).length
              ? `${label} (${value.length})`
              : `${label} (all)`}
          </span>

          <span className="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
            <ChevronUpDownIcon
              className="h-5 w-5 text-gray-400"
              aria-hidden="true"
            />
          </span>
        </Listbox.Button>
        <Transition
          as={Fragment}
          leave="transition ease-in duration-100"
          leaveFrom="opacity-100"
          leaveTo="opacity-0"
        >
          <Listbox.Options className="absolute mt-1 max-h-60 w-full overflow-auto rounded-lg border border-sky-500 bg-white py-1 text-base text-sm ring-1 ring-black ring-opacity-5 focus:outline-none">
            {Object.entries(options).map(([key, optionValue]) => {
              const isSelected = value.includes(key);

              return (
                <Listbox.Option
                  key={key}
                  className="relative cursor-pointer select-none py-2 pl-10 pr-4 text-gray-900"
                  value={key}
                >
                  {({ selected }) => (
                    <>
                      <span
                        className={`block truncate ${
                          selected ? "font-medium" : "font-normal"
                        }`}
                      >
                        {displayValueName ? optionValue.name : optionValue}
                      </span>
                      {isSelected && selected ? (
                        <span className="absolute inset-y-0 left-0 flex items-center pl-3 text-sky-500">
                          <CheckIcon className="h-5 w-5" aria-hidden="true" />
                        </span>
                      ) : null}
                    </>
                  )}
                </Listbox.Option>
              );
            })}
          </Listbox.Options>
        </Transition>
      </div>
    </Listbox>
  );
}

export default function App() {
  const [data, setData] = useState([]);
  // have all years and conferences selected by default
  const [selectedYears, setSelectedYears] = useState(
    Object.keys(years).map(Number),
  );
  const [selectedConferences, setSelectedConferences] = useState(
    Object.keys(conferences).map(Number),
  );

  const [selectedPaper, setSelectedPaper] = useState(null);
  const [selectedFeature, setSelectedFeature] = useState(null);
  const [zoomCoordinates, setZoomCoordinates] = useState(null);
  const [searchTerm, setSearchTerm] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [showAbstractTextbox, setShowAbstractTextbox] = useState(false);
  const [abstractValue, setAbstractValue] = useState("");
  const [isSpecialPaperSelected, setIsSpecialPaperSelected] = useState(true);
  const [massHighlightPoints, setMassHighlightPoints] = useState([]);
  const [showingAbstract, setShowingAbstract] = useState(false);
  const [showingMap, setShowingMap] = useState(true);
  const [resetHighlight, setResetHighlight] = useState(false);
  const containerRef = useRef(null);

  useEffect(() => {
    setSelectedYears(Object.keys(years).map(String));
    setSelectedConferences(Object.keys(conferences).map(String));
  }, []);

  useEffect(() => {
    getData()
      .then((data) => {
        if (data) {
          setData(data);
        }
      })
      .catch((error) => {});
  }, []);

  useEffect(() => {
    function handleClickOutside(event) {
      if (
        containerRef.current &&
        !containerRef.current.contains(event.target)
      ) {
        setSearchResults([]);
      }
    }

    document.addEventListener("click", handleClickOutside);
    return () => {
      document.removeEventListener("click", handleClickOutside);
    };
  }, []);

  if (!data) {
    return null;
  }

  const handlePointClick = async (paperId, featureName) => {
    if (paperId && paperId === -1) {
      // clicked on point from uploaded abstract
      return;
    }
    setSelectedPaper(null);
    setSelectedFeature(null);
    setIsSpecialPaperSelected(false);
    if (paperId) {
      try {
        const paper = await getPaper(paperId); // fetch paper details using getPaper function
        setSelectedPaper(paper);
        setSelectedFeature(featureName);
        setShowingAbstract(false);
      } catch (error) {}
    }
  };

  const resetSpecialPaper = () => {
    setSelectedPaper(null);
    setSelectedFeature(null);
    setShowingAbstract(false);
    setMassHighlightPoints([]);
    setResetHighlight(true);
    setIsSpecialPaperSelected(false);
  };

  const handleZoom = (xRange, yRange) => {
    setZoomCoordinates({ xRange, yRange });
  };

  const [showInstructionPopup, setShowInstructionPopup] = useState(
    !localStorage.getItem("hasVisited"),
  );

  useEffect(() => {
    localStorage.setItem("hasVisited", true);
  }, []);

  const handleCloseInstructionPopup = () => {
    setShowInstructionPopup(false);
  };

  const handleSearch = async () => {
    try {
      const results = await postSearch(searchTerm);
      setSearchResults(results);
    } catch (error) {}
  };
  const updateShowingMap = (newValue) => {
    setShowingMap(newValue);
  };

  const handleSearchResultClick = async (paperId) => {
    try {
      const paper = await getPaper(paperId);
      setSelectedPaper(paper);
      setSelectedFeature(null);
      setIsSpecialPaperSelected(true);
      setShowingAbstract(false);
      setResetHighlight(false);
      // find all of the features to be highlighted
      // year
      const p_year = paper.published_location_year;
      // conference
      const p_conference = paper.published_location_code;
      // get appropriate year + conference indices
      const p_conf_ind = Object.keys(conferences).find(
        (key) => conferences[key].name === p_conference,
      );
      const p_year_ind = Object.keys(years).find(
        (key) => years[key] === p_year,
      );
      // bucket to search
      const bucket_to_search = data[p_conf_ind][p_year_ind];
      const matches = bucket_to_search.filter(
        (entry) => entry.hash === paperId,
      );
      setMassHighlightPoints(matches);
      const delayDuration = 800;
      setTimeout(() => {
        setShowingMap(true);
      }, delayDuration);
    } catch (error) {}
  };

  const handleToggleSidebar = () => {
    setShowingMap(!showingMap);
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter") {
      handleSearch();
    }
  };

  const handleAbstractButtonClick = () => {
    setShowAbstractTextbox(true);
  };

  const handleSubmitAbstract = () => {
    if (!abstractValue.trim()) {
      alert("Please enter a valid abstract.");
      return;
    }
    setShowAbstractTextbox(false);

    postAbstract(abstractValue)
      .then((response) => {
        if (!response || !response.features) {
          return;
        }
        setAbstractValue("");
        setShowAbstractTextbox(false);
        setIsSpecialPaperSelected(true);
        setShowingAbstract(true);
        setSelectedFeature(null);
        const my_paper = {
          title: "Your Abstract",
          abstract: abstractValue.trim(),
          features: response.features,
        };
        setSelectedPaper(my_paper);
        const myHighlightPoints = [];
        for (let i = 0; i < response.features.length; i++) {
          const new_entry = {
            feature: response.features[i],
            x: response.embeddings[i][0],
            y: response.embeddings[i][1],
            hash: -1,
          };
          myHighlightPoints.push(new_entry);
        }
        setMassHighlightPoints(myHighlightPoints);
        const delayDuration = 800;
        setTimeout(() => {
          setShowingMap(true);
        }, delayDuration);
      })
      .catch((error) => {});
  };

  const handleCloseAbstractForm = () => {
    setShowAbstractTextbox(false);
    return;
  };

  return (
    <main
      className={`min-w-screen flex h-full min-h-screen w-full flex-row items-center space-x-0 overflow-hidden bg-slate-200 ${
        showAbstractTextbox && !showingMap ? "abstract-bg-kludge" : ""
      }`}
    >
      <div
        className={`flex h-full w-full bg-white ${
          showingMap
            ? " embedding-visualization-container "
            : " embedding-visualization-sidebar "
        }`}
        style={{ cursor: "pointer" }}
      >
        <div className="logo-container">
          <a href="https://mlmap.xyz" target="_blank" rel="noopener noreferrer">
            <h2 className="m-2 text-center text-2xl font-bold">MLMap.xyz</h2>
          </a>
        </div>
        <div className="menu-button" onClick={handleToggleSidebar}>
          <i className="fas fa-bars"></i>
        </div>
        <EmbeddingVisualization
          data={data}
          onPointClick={handlePointClick}
          selectedYears={selectedYears}
          selectedConferences={selectedConferences}
          onZoom={handleZoom}
          zoomCoordinates={zoomCoordinates}
          highlightedPoints={massHighlightPoints}
          showingAbstract={showingAbstract}
          setShowingMap={updateShowingMap}
          resetHighlight={resetHighlight}
        />
      </div>
      <div
        style={{ width: "max-content" }}
        className={`flex min-w-max flex-col items-center justify-center bg-slate-200 font-inter text-crisp-white ${
          !showingMap
            ? "embedding-visualization-container"
            : "embedding-visualization-sidebar"
        }`}
      >
        <div className="menu-button text-black" onClick={handleToggleSidebar}>
          <i className="fas fa-bars"></i>
        </div>

        <div className="floating-sidebar-fullscreen rounded-lg bg-slate-200 opacity-100 md:max-w-6xl">
          <div className="flex flex-col items-center justify-center p-2">
            <div className="relative w-full" ref={containerRef}>
              <div className="flex items-center justify-center">
                <input
                  type="text"
                  className="flex-grow rounded-l-lg px-4 py-2 text-black"
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Search for a paper..."
                  style={{
                    outline: "none",
                    borderBottomRightRadius:
                      searchResults.length > 0 ? "0" : "",
                    borderBottomLeftRadius: searchResults.length > 0 ? "0" : "",
                  }}
                />
                <button
                  className="rounded-r-lg bg-sky-500 px-4 py-2 font-semibold text-white hover:bg-sky-600"
                  onClick={handleSearch}
                  style={{
                    outline: "none",
                    borderBottomLeftRadius: searchResults.length > 0 ? "0" : "",
                    borderBottomRightRadius:
                      searchResults.length > 0 ? "0" : "",
                  }}
                >
                  Search
                </button>
              </div>
              {searchResults.length > 0 && (
                <div
                  className="search-results-container absolute left-0 top-full z-50 max-h-60 w-full overflow-auto rounded-lg border border-sky-500 bg-white"
                  style={{
                    maxHeight: "250px",
                    borderTopLeftRadius: "0",
                    borderTopRightRadius: "0",
                    borderBottomRightRadius: "0.5rem",
                    borderBottomLeftRadius: "0.5rem",
                  }}
                >
                  {searchResults.map((result, index) => (
                    <div
                      key={index}
                      onClick={() => {
                        handleSearchResultClick(result[1]);
                        setSearchResults([]);
                      }}
                      className="cursor-pointer p-2 text-black hover:bg-sky-500 hover:bg-opacity-75 hover:text-white hover:text-white"
                    >
                      <h3 className="text-sm font-semibold">{result[0]}</h3>
                    </div>
                  ))}
                </div>
              )}
            </div>

            <div className="flex w-full flex-row items-center justify-between font-inter text-4xl font-bold text-black">
              <CustomListbox
                value={selectedYears}
                onChange={setSelectedYears}
                options={years}
                label="Years"
                displayValueName={false}
                className="mr-[5px] w-5/12"
              />

              <CustomListbox
                value={selectedConferences}
                onChange={setSelectedConferences}
                options={conferences}
                label="Conferences"
                displayValueName={true}
                className="ml-[5px] w-7/12"
              />
            </div>

            <div className="my-2.5">
              <div className="h-96 w-80 overflow-auto rounded-lg bg-white p-4 font-inter">
                {selectedPaper ? (
                  <div>
                    {isSpecialPaperSelected && (
                      <button
                        className="float-right rounded-lg p-2 text-gray-700"
                        onClick={resetSpecialPaper}
                      >
                        <svg
                          className="h-4 w-4"
                          viewBox="0 0 20 20"
                          fill="currentColor"
                          aria-hidden="true"
                        >
                          <path
                            fillRule="evenodd"
                            d="M14.293 5.293a1 1 0 011.414 1.414L11.414 12l4.293 4.293a1 1 0 01-1.414 1.414L10 13.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 12 4.293 7.707a1 1 0 111.414-1.414L10 10.586l4.293-4.293z"
                            clipRule="evenodd"
                          />
                        </svg>
                      </button>
                    )}
                    <h3 className="mb-2 text-xl font-bold text-black">
                      {selectedPaper.title}
                    </h3>
                    {selectedFeature && (
                      <p className="mb-1 text-sm text-gray-600">
                        <b>Selected Feature:</b>{" "}
                        {selectedFeature
                          .split(" ")
                          .map(
                            (word) =>
                              word.charAt(0).toUpperCase() + word.slice(1),
                          )
                          .join(" ")}
                      </p>
                    )}
                    {selectedPaper.authors &&
                      selectedPaper.authors.length > 0 && (
                        <p className="mb-1 text-sm text-gray-600">
                          <b>Authors:</b> {selectedPaper.authors.join(", ")}
                        </p>
                      )}
                    {selectedPaper.published_location_year && (
                      <p className="mb-1 text-sm text-gray-600">
                        <b>Publication Year:</b>{" "}
                        {selectedPaper.published_location_year}
                      </p>
                    )}
                    {selectedPaper.published_location_code && (
                      <p className="mb-1 text-sm text-gray-600">
                        <b>Publication Location:</b>{" "}
                        {selectedPaper.published_location_code}
                      </p>
                    )}
                    <p className="mb-2 text-sm text-gray-600">
                      <b>Abstract:</b> {selectedPaper.abstract}
                    </p>
                    {selectedPaper.features && (
                      <div className="mb-1 text-sm text-gray-600">
                        <b>Features:</b>
                        <ul
                          style={{
                            listStyleType: "square",
                            marginLeft: "1rem",
                          }}
                        >
                          {selectedPaper.features.map((feature) => {
                            const words = feature.split(" ");
                            const capitalizedWords = words.map((word) => {
                              if (word.charAt(0) === "(") {
                                return word;
                              } else {
                                return (
                                  word.charAt(0).toUpperCase() +
                                  word.slice(1).toLowerCase()
                                );
                              }
                            });
                            const capitalizedFeature =
                              capitalizedWords.join(" ");
                            return <li key={feature}>{capitalizedFeature}</li>;
                          })}
                        </ul>
                      </div>
                    )}

                    {selectedPaper.external_links &&
                      selectedPaper.external_links.length > 0 && (
                        <div className="w-full">
                          <a
                            href={
                              selectedPaper.published_location_code === "ACL"
                                ? selectedPaper.external_links[0]["PDF"]
                                : selectedPaper.external_links.find(
                                    (link) =>
                                      link?.href_text &&
                                      (link.href_text.toLowerCase() === "pdf" ||
                                        link.href_text.toLowerCase() ===
                                          "paper" ||
                                        link.href_text.toLowerCase() ===
                                          "download pdf"),
                                  )?.href
                            }
                            target="_blank"
                            rel="noopener noreferrer"
                            className="mt-2 block w-full rounded-lg bg-green-600 px-4 py-2 text-center font-bold text-white"
                          >
                            Read Paper
                          </a>
                        </div>
                      )}
                  </div>
                ) : (
                  <div className="flex h-full items-center justify-center">
                    <p className="text-gray-600">No paper selected</p>
                  </div>
                )}
              </div>
            </div>

            <div className="flex flex-col items-center justify-center font-inter text-black">
              <button
                className="w-80 rounded-lg bg-sky-500 px-4 py-2 font-bold text-white hover:bg-sky-600"
                onClick={handleAbstractButtonClick}
              >
                Explore Your Abstract
              </button>
              {showAbstractTextbox && (
                <AbstractForm
                  abstractValue={abstractValue}
                  onChange={(e) => setAbstractValue(e.target.value)}
                  onSubmit={handleSubmitAbstract}
                  onClose={handleCloseAbstractForm}
                />
              )}
            </div>

            <div className="flex flex-col items-center justify-center text-black"></div>
          </div>
        </div>
      </div>
      {showInstructionPopup && (
        <InstructionPopup onClose={handleCloseInstructionPopup} />
      )}
    </main>
  );
}
