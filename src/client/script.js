function parse(value) {
  const parsed = parseFloat(value);
  if (Number.isNaN(parsed)) {
    return null;
  }
  return parsed;
}

function mapWithNulls(data, selector, fn = null) {
  return data.map((row) => {
    const entry = selector(row);
    if (entry != null && !Number.isNaN(entry)) {
      if (fn == null) {
        return entry;
      }
      return fn(entry);
    }
    return null;
  });
}

async function getCSV() {
  const url = "data_60m.txt?time" + encodeURIComponent(Date.now());
  const res = await fetch(url);
  document.getElementById("download").setAttribute("href", url);
  const text = await res.text();
  const rows = text.split("\n");

  return rows.map((row) => {
    const [currentTime, voltage0, voltage1, instantaneous, total] = row.split(
      ","
    );

    return {
      time: new Date(Date.now() + 1000 * parse(currentTime)),
      voltage0: parse(voltage0),
      voltage1: parse(voltage1),
      instantaneous: parse(instantaneous),
      total: parse(total),
    };
  });
}

const chartsInOrder = [];
let index = 0;

function nextChart() {
  if (index < chartsInOrder.length) {
    return chartsInOrder[index++];
  }

  const root = document.getElementById("charts");
  const el = document.createElement("div");
  root.appendChild(el);
  chartsInOrder[index++] = el;
  return el;
}

async function delay(time) {
  return new Promise((resolve) => setTimeout(resolve, time));
}
async function animationFrame() {
  return new Promise((resolve) => requestAnimationFrame(resolve));
}

async function run(
  minLevelVoltage,
  maxLevelVoltage,
  fullScalePressure,
  densityOfWater,
  timeRange,
  injectorHoleCount,
  injectorHoleDiameter,
  flowCalibration
) {
  let rows = await getCSV();

  rows = rows.slice(-Math.round((rows.length * timeRange) / 100));

  await animationFrame();
  Plotly.newPlot(
    nextChart(),
    [
      {
        type: "scatter",
        x: mapWithNulls(rows, (row) => row.time),
        y: mapWithNulls(
          rows,
          (row) => row.voltage0,
          (voltage) =>
            ((voltage - minLevelVoltage) /
              (maxLevelVoltage - minLevelVoltage)) *
            fullScalePressure
        ),
      },
    ],
    {
      title: "Transducer Pressure",
      yaxis: {
        title: "pressure (bar)",
      },
    }
  );

  await animationFrame();
  Plotly.newPlot(
    nextChart(),
    [
      {
        type: "scatter",
        x: mapWithNulls(rows, (row) => row.time),
        y: mapWithNulls(
          rows,
          (row) => row.instantaneous,
          (entry) => (((entry * densityOfWater) / 1e3) * flowCalibration) / 100
        ),
      },
    ],
    {
      title: "Flow (current)",
      yaxis: {
        title: "mass flow (kg/s)",
      },
    }
  );
  const pressures = mapWithNulls(
    rows,
    (row) => row.voltage0,
    (voltage) =>
      ((voltage - minLevelVoltage) / (maxLevelVoltage - minLevelVoltage)) *
      fullScalePressure
  );

  const pressureValues = [];
  const minP = Math.min(0, ...pressures);
  const maxP = Math.max(5, ...pressures);
  for (let p = minP; p <= maxP; p += (maxP - minP) / 501) {
    pressureValues.push(p);
  }

  await animationFrame();
  Plotly.newPlot(
    nextChart(),
    [
      {
        type: "scatter",
        x: pressures,
        y: mapWithNulls(
          rows,
          (row) => row.instantaneous,
          (entry) => (((entry * densityOfWater) / 1e3) * flowCalibration) / 100
        ),
        mode: "markers",
        name: "Measured",
      },
      ...[0.25, 0.5, 0.75, 1].map((cD) => {
        const numHoles = injectorHoleCount;
        const holeDiameterMm = injectorHoleDiameter;
        const area =
          numHoles * Math.pow(holeDiameterMm / 1000.0 / 2.0, 2.0) * Math.PI;
        return {
          type: "scatter",
          x: pressureValues,
          y: pressureValues.map(
            (el) => cD * area * Math.sqrt(2 * densityOfWater * el * 1e5)
          ),
          mode: "line",
          line: {
            dash: "dot",
            width: 2,
          },
          name: `Cd = ${cD.toFixed(2)}`,
        };
      }),
    ],
    {
      title: "Flow (total)",
      yaxis: {
        title: "mass flow (kg)",
      },
      xaxis: {
        title: "pressure (bar)",
      },
    }
  );

  await animationFrame();
  Plotly.newPlot(
    nextChart(),
    [
      {
        type: "scatter",
        x: mapWithNulls(rows, (row) => row.time),
        y: mapWithNulls(
          rows,
          (row) => row.instantaneous,
          (row) => (row * flowCalibration) / 100
        ),
      },
    ],
    {
      title: "Flow (current)",
      yaxis: {
        title: "volumetric flow (l/s)",
      },
    }
  );
  await animationFrame();
  Plotly.newPlot(
    nextChart(),
    [
      {
        type: "scatter",
        x: mapWithNulls(rows, (row) => row.time),
        y: mapWithNulls(
          rows,
          (row) => row.total,
          (row) => (row * flowCalibration) / 100
        ),
      },
    ],
    {
      title: "Flow (total)",
      yaxis: {
        title: "volumetric flow (l)",
      },
    }
  );

  await animationFrame();
  Plotly.newPlot(
    nextChart(),
    [
      {
        type: "scatter",
        x: mapWithNulls(rows, (row) => row.time),
        y: mapWithNulls(
          rows,
          (row) => row.total,
          (entry) => (((entry * densityOfWater) / 1e3) * flowCalibration) / 100
        ),
      },
    ],
    {
      title: "Flow (total)",
      yaxis: {
        title: "mass flow (kg)",
      },
    }
  );
  await animationFrame();
  Plotly.newPlot(
    nextChart(),
    [
      {
        type: "scatter",
        x: mapWithNulls(rows, (row) => row.time),
        y: mapWithNulls(rows, (row) => row.voltage0),
      },
    ],
    {
      title: "Transducer Voltage",
      yaxis: {
        title: "voltage (V)",
      },
    }
  );

  const rowsWithZeroFlow = rows.filter(
    (row) => Math.abs(row.instantaneous) < 1e-6
  );
  await animationFrame();
  Plotly.newPlot(
    nextChart(),
    [
      {
        type: "histogram",
        x: mapWithNulls(rowsWithZeroFlow, (row) => row.voltage0),
        histnorm: "probability",
        cumulative: { enabled: true },
      },
    ],
    {
      title: "Transducer Zero-Flow Voltage",
      xaxis: {
        title: "voltage (V)",
      },
    }
  );
  await animationFrame();
  Plotly.newPlot(
    nextChart(),
    [
      {
        type: "histogram",
        x: mapWithNulls(
          rowsWithZeroFlow,
          (row) => row.voltage0,
          (voltage) =>
            ((voltage - minLevelVoltage) /
              (maxLevelVoltage - minLevelVoltage)) *
            fullScalePressure *
            1000
        ),
        histnorm: "probability",
        cumulative: { enabled: true },
      },
    ],
    {
      title: "Transducer Zero-Flow Pressure",
      xaxis: {
        title: "pressure (mbar)",
      },
    }
  );

  await animationFrame();
  Plotly.newPlot(
    nextChart(),
    [
      {
        type: "scatter",
        x: mapWithNulls(rows, (row) => row.time),
        y: mapWithNulls(
          rows,
          (row) => row.voltage1,
          (voltage) => (1000 * (5 - voltage)) / 2
        ),
      },
    ],
    {
      yaxis: {
        title: "voltage (mV)",
      },
      title: "Voltage Drop",
    }
  );

  await animationFrame();
  Plotly.newPlot(
    nextChart(),
    [
      {
        type: "scatter",
        x: mapWithNulls(rows, (row) => row.time),
        y: mapWithNulls(
          rows,
          (row) => row.voltage0,
          (voltage) =>
            (voltage - minLevelVoltage) / (maxLevelVoltage - minLevelVoltage)
        ),
      },
    ],
    {
      title: "Transducer Full Scale Ratio",
      yaxis: {
        title: "ratio",
      },
    }
  );

  const xValues = [];
  const yValues = [];
  for (let x = 0; x < 15; x += 1e-2) {
    xValues.push(x);
    const y =
      (x / fullScalePressure) * (maxLevelVoltage - minLevelVoltage) +
      minLevelVoltage;
    if (y >= 5) continue;
    yValues.push(y);
  }

  await animationFrame();
  Plotly.newPlot(
    document.getElementById("calibrationPlot"),
    [
      {
        type: "scatter",
        x: xValues,
        y: yValues,
      },
    ],
    {
      title: "Calibrated Pressure",
      xaxis: {
        title: "pressure (bar)",
      },
      yaxis: {
        title: "voltage (V)",
        max: 5,
        min: 0,
      },
    }
  );
}

const inputs = [];
function setupLocalStorageInput(id) {
  const el = document.getElementById(id);
  const defaultValue = parse(el.getAttribute("default-value"));
  const val = parse(localStorage.getItem(id));
  if (val == null) {
    localStorage.setItem(id, defaultValue);
    el.value = defaultValue;
  } else {
    el.value = val;
  }

  const obj = {
    reset: () => {
      el.value = defaultValue;
      localStorage.setItem(id, defaultValue);
    },
    save: () => {
      const value = el.value;
      localStorage.setItem(id, value);
    },
    get value() {
      return val;
    },
  };
  inputs.push(obj);

  return obj.value;
}
document.getElementById("resetCalibration").addEventListener("click", () => {
  for (const inp of inputs) {
    inp.reset();
  }
  window.location.reload();
});
document.getElementById("saveCalibration").addEventListener("click", () => {
  for (const inp of inputs) {
    inp.save();
  }
  window.location.reload();
});

const zeroFlowVoltage = setupLocalStorageInput("zeroFlowVoltage");
const peakPressure = setupLocalStorageInput("peakPressure");
const peakPressureVoltage = setupLocalStorageInput("peakPressureVoltage");
const densityOfWater = setupLocalStorageInput("densityOfWater");
const timeRange = setupLocalStorageInput("timeRange");
const injectorHoleCount = setupLocalStorageInput("injectorHoleCount");
const injectorHoleDiameter = setupLocalStorageInput("injectorHoleDiameter");
const flowCalibration = setupLocalStorageInput("flowCalibration");

const refreshButton = document.getElementById("refresh");
async function main() {
  try {
    index = 0;
    await run(
      zeroFlowVoltage,
      peakPressure,
      peakPressureVoltage,
      densityOfWater,
      timeRange,
      injectorHoleCount,
      injectorHoleDiameter,
      flowCalibration
    );
  } catch (err) {
    alert(err.stack);
  }
}

refreshButton.disabled = true;
main().then(() => {
  refreshButton.disabled = false;
});

refreshButton.addEventListener("click", () => {
  refreshButton.disabled = true;
  main().then(() => {
    refreshButton.disabled = false;
  });
});
