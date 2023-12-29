import {createSlice} from '@reduxjs/toolkit';

const initialState = {
  recentFiles: [],
};

const fileSlice = createSlice({
  name: 'privacy',
  initialState,
  reducers: {
    setRecentFiles: (state, action) => {
      return {...state, recentFiles: action.payload};
    },
  },
});

export default fileSlice;
