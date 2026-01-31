import { createStore } from "/js/AlpineStore.js";

// define the model object holding data and functions
const model = {
  connected: false,
  progressActive: false,  // true when agent is working
};

// convert it to alpine store
const store = createStore("chatTop", model);

// export for use in other files
export { store };
