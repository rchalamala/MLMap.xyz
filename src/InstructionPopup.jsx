import { useState } from "react";

const InstructionPopup = ({ onClose }) => {
  return (
    <div className="fixed inset-0 flex items-center justify-center bg-black bg-opacity-75">
      <div className="responsive-instruction-box relative rounded-lg bg-slate-200 p-4 shadow-lg">
        <button
          className="absolute right-2 top-2 text-gray-600 hover:text-gray-800"
          onClick={onClose}
        >
          &#10005;
        </button>
        <h2 className="mb-4 text-center font-inter text-xl font-bold">
          Welcome to MLMap.xyz!
        </h2>
        <div className="text-center font-inter text-gray-700">
          Dive into our interactive embedding map to explore the ever-changing
          artificial intelligence landscape and gain valuable insights into key
          features discussed across publications. Uncover new perspectives,
          search for relevant papers, and upload your own abstract to align your
          work with existing conference and feature clusters.
          <br />
          <br />
          <b>
            Due to hosting costs, support for MLMap.xyz has ended. We hope you
            enjoyed our service!
          </b>
          <br />
          <br />
          <a
            href="https://github.com/rchalamala/MLMap.xyz"
            target="_blank"
            rel="noopener noreferrer"
            className="text-center font-inter text-blue-500 hover:underline"
          >
            View the source code here.
          </a>
        </div>
        <div className="mt-4 flex justify-center">
          <button
            className="rounded-lg bg-sky-500 px-4 py-2 font-semibold text-white hover:bg-sky-600"
            onClick={onClose}
          >
            Start Exploring
          </button>
        </div>
      </div>
    </div>
  );
};

export default InstructionPopup;
