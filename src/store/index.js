import {configureStore, combineReducers} from '@reduxjs/toolkit';
import filesSlice from './slices/files';

const rootReducer = combineReducers({
  files: filesSlice.reducer,
});

const store = configureStore({
  reducer: rootReducer,
});

export default store;
