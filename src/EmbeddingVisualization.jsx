import { useEffect, useState } from "react";
import Plot from "react-plotly.js";

export const years = {
  0: 2013,
  1: 2014,
  2: 2015,
  3: 2016,
  4: 2017,
  5: 2018,
  6: 2019,
  7: 2020,
  8: 2021,
  9: 2022,
  10: 2023,
};

export const conferences = {
  0: { name: "ACL", color: "#8aed9b" },
  1: { name: "CVPR", color: "#f08bee" },
  2: { name: "ICCV", color: "#4895e8" },
  3: { name: "ICML", color: "#ffcd82" },
  4: { name: "NeurIPS", color: "#ff788c" },
};

const EmbeddingVisualization = ({
  data,
  onPointClick,
  selectedYears,
  selectedConferences,
  onZoom,
  zoomCoordinates,
  highlightedPoints,
  showingAbstract,
  setShowingMap,
  resetHighlight,
}) => {
  const [hasRandomizedLoad, setHasRandomizedLoad] = useState(false);
  const [renderOrder, setRenderOrder] = useState([]);
  const [kludge, setKludge] = useState(false);
  const [zoomLevel, setZoomLevel] = useState(1);

  useEffect(() => {
    setKludge(false);
  }, [resetHighlight]);

  useEffect(() => {
    if (!hasRandomizedLoad) {
      const orderArray = [];
      for (const conference in conferences) {
        for (const year in years) {
          orderArray.push([conference, year]);
        }
      }
      orderArray.sort(() => Math.random() - 0.5);
      setRenderOrder(orderArray);
      setHasRandomizedLoad(true);
    }
  }, [hasRandomizedLoad]);

  const [figure, setFigure] = useState({
    data: [],
    layout: {
      autosize: true,
      margin: { t: 0, r: 0, l: 0, b: 0 },
      hovermode: "closest",
      xaxis: {
        automargin: true,
        showgrid: false,
        zeroline: false,
        showticklabels: false,
        ticks: "",
        range: zoomCoordinates?.xRange || [-10, 10],
      },
      yaxis: {
        automargin: true,
        showgrid: false,
        zeroline: false,
        showticklabels: false,
        ticks: "",
        range: zoomCoordinates?.yRange || [-10, 10],
      },
      dragmode: "pan",
      showlegend: false,
      legend: {
        itemclick: false,
        itemdoubleclick: false,
      },
    },

    config: {
      scrollZoom: true,
      displayModeBar: false,
    },
  });

  const [allTraces, setAllTraces] = useState([]);
  // make a trace for each year/conference combination, then enable/disable traces when selected
  useEffect(() => {
    const traces = [];
    let xMin, xMax, yMin, yMax;

    if (data.length > 0) {
      for (const conference in conferences) {
        const row = [];
        for (const year in years) {
          const traceData = data[conference][year];
          const xs = traceData.map((d) => d.x);
          const ys = traceData.map((d) => d.y);

          if (xMin === undefined || Math.min(...xs) < xMin)
            xMin = Math.min(...xs);
          if (xMax === undefined || Math.max(...xs) > xMax)
            xMax = Math.max(...xs);
          if (yMin === undefined || Math.min(...ys) < yMin)
            yMin = Math.min(...ys);
          if (yMax === undefined || Math.max(...ys) > yMax)
            yMax = Math.max(...ys);

          row.push({
            x: xs,
            y: ys,
            mode: "markers",
            type: "scattergl",
            opacity: 0.7,
            name: conferences[conference].name,
            marker: { color: conferences[conference].color, size: 4 },
            hoverinfo: "text",
            text: traceData.map((d) =>
              d.feature
                .split(" ")
                .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
                .join(" "),
            ),
            hash: traceData.map((d) => d.hash),
          });
        }
        traces.push(row);
      }
      setAllTraces(traces);
    }

    setFigure((f) => ({
      ...f,
      layout: {
        ...f.layout,
        xaxis: {
          ...f.layout.xaxis,
          range: zoomCoordinates?.xRange || [xMin, xMax],
        },
        yaxis: {
          ...f.layout.yaxis,
          range: zoomCoordinates?.yRange || [yMin, yMax],
        },
      },
    }));
  }, [data]);

  const [clickedPoint, setClickedPoint] = useState(null);

  const handlePointClick = (event) => {
    if (event.points.length > 0) {
      setKludge(true);
      const clickedData = event.points[0].data;
      const clickedIndex = event.points[0].pointIndex;
      const paperId = clickedData.hash[clickedIndex];
      const featureName = clickedData.text[clickedIndex];
      const xCoord = clickedData.x[clickedIndex];
      const yCoord = clickedData.y[clickedIndex];
      setClickedPoint({
        x: xCoord,
        y: yCoord,
        hash: paperId,
        feature: featureName,
      });
      onPointClick(paperId, featureName);
      const delayDuration = 800;
      setTimeout(() => {
        setShowingMap(false);
      }, delayDuration);
    }
  };

  const handleZoom = (event) => {
    if (
      event &&
      event["xaxis.range[0]"] &&
      event["xaxis.range[1]"] &&
      event["yaxis.range[0]"] &&
      event["yaxis.range[1]"]
    ) {
      const xRange = [event["xaxis.range[0]"], event["xaxis.range[1]"]];
      const yRange = [event["yaxis.range[0]"], event["yaxis.range[1]"]];
      onZoom(xRange, yRange);
    }
  };

  useEffect(() => {
    if (highlightedPoints && highlightedPoints.length > 0) {
      setClickedPoint(null);
    }
  }, [highlightedPoints]);

  useEffect(() => {
    const traces = [];

    if (allTraces.length > 0) {
      for (const conference in conferences) {
        for (const year in years) {
          const trace = allTraces[conference][year];
          trace.showlegend = false;
        }
      }

      renderOrder.forEach(([conference, year]) => {
        if (
          selectedConferences.includes(conference) &&
          selectedYears.includes(year)
        ) {
          const trace = allTraces[conference][year];
          traces.push(trace);
        }
      });

      // selected point traced
      if (clickedPoint) {
        const clicked_point_trace = {
          x: [clickedPoint.x],
          y: [clickedPoint.y],
          mode: "markers",
          type: "scattergl",
          name: "Selected Feature",
          marker: {
            color: "rgb(105,105,105)",
            size: 10,
            symbol: "circle-open",
            line: { color: "rgb(105,105,105)", width: 3 },
          },
          hoverinfo: "text",
          text: [
            clickedPoint.feature
              .split(" ")
              .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
              .join(" "),
          ],
          hash: [clickedPoint.hash],
        };
        traces.push(clicked_point_trace);
      }

      if (
        !clickedPoint &&
        highlightedPoints &&
        highlightedPoints.length > 0 &&
        !showingAbstract
      ) {
        // trace for all of the highlighted points
        const highlighted_points_trace = {
          x: highlightedPoints.map((point) => point.x),
          y: highlightedPoints.map((point) => point.y),
          mode: "markers",
          type: "scattergl",
          name: "Highlighted Points",
          marker: {
            color: "rgb(105,105,105)",
            size: 10,
            symbol: "circle-open",
            line: { color: "rgb(105,105,105)", width: 3 },
          },
          hoverinfo: "text",
          text: highlightedPoints.map((point) =>
            point.feature
              .split(" ")
              .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
              .join(" "),
          ),
          hash: highlightedPoints.map((point) => point.hash),
        };
        traces.push(highlighted_points_trace);
      }

      if (
        !clickedPoint &&
        highlightedPoints &&
        highlightedPoints.length > 0 &&
        showingAbstract
      ) {
        // trace for points from abstract
        const highlighted_points_trace = {
          x: highlightedPoints.map((point) => point.x),
          y: highlightedPoints.map((point) => point.y),
          mode: "markers",
          type: "scattergl",
          name: "Highlighted Points",
          marker: { color: "#ff8c44", size: 4 },
          hoverinfo: "text",
          text: highlightedPoints.map((point) =>
            point.feature
              .split(" ")
              .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
              .join(" "),
          ),
          hash: highlightedPoints.map((point) => point.hash),
        };

        const highlighted_points_highlight = {
          x: highlightedPoints.map((point) => point.x),
          y: highlightedPoints.map((point) => point.y),
          mode: "markers",
          type: "scattergl",
          name: "Highlighted Points",
          marker: {
            color: "rgb(105,105,105)",
            size: 10,
            symbol: "circle-open",
            line: { color: "rgb(105,105,105)", width: 3 },
          },
          hoverinfo: "text",
          text: highlightedPoints.map((point) =>
            point.feature
              .split(" ")
              .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
              .join(" "),
          ),
          hash: highlightedPoints.map((point) => point.hash),
        };

        traces.push(highlighted_points_trace);
        traces.push(highlighted_points_highlight);
      }
    }

    setFigure((f) => ({
      ...f,
      data: traces,
    }));
  }, [
    allTraces,
    selectedYears,
    selectedConferences,
    clickedPoint,
    highlightedPoints,
  ]);

  return (
    <div className="h-screen w-full">
      {data.length > 0 ? (
        <div>
          <Plot
            className="h-screen w-full"
            data={figure.data}
            layout={figure.layout}
            config={{ scrollZoom: true, displayModeBar: false }}
            useResizeHandler={true}
            onClick={handlePointClick}
            onRelayout={handleZoom}
          />
          <div className="legend-container">
            <div
              className={`flex ${
                showingAbstract ? "vertical-legend" : "flex-row"
              } gap-3`}
            >
              {Object.entries(conferences).map(
                ([key, value]) =>
                  selectedConferences.includes(key) && (
                    <div key={key} className="flex items-center">
                      <span
                        className="mr-1 h-4 w-4 rounded-full"
                        style={{ backgroundColor: value.color }}
                      />
                      <span className="">{value.name}</span>
                    </div>
                  ),
              )}
              {showingAbstract && (
                <div className="flex items-center">
                  <span
                    className="mr-1 h-4 w-4 rounded-full"
                    style={{ backgroundColor: "#ff8c44" }}
                  />
                  <span className="">Your Abstract</span>
                </div>
              )}
            </div>
          </div>
        </div>
      ) : (
        <div className="flex h-full items-center justify-center">
          {Object.entries(selectedYears).some((y) => y.year % 2 === 0) &&
          Object.entries(selectedConferences).some(
            ([, value]) =>
              value.name === "ICCV" &&
              Object.keys(selectedConferences).length <
                Object.keys(conferences).length,
          ) ? (
            <p className="text-black-500 text-2xl font-bold">
              No Data to Display - Note That ICCV Only Meets Odd Years
            </p>
          ) : (
            <p className="text-black-500 text-2xl font-bold text-black">
              No Data to Display
            </p>
          )}
        </div>
      )}
    </div>
  );
};

export default EmbeddingVisualization;
