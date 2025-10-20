import React from "react";

function SidePanel() {
    const [open, setOpen] = React.useState(true);

  return (
      <>
      <button
          type="button"
          aria-expanded={open}
          aria-controls="app-side-panel"
          onClick={() => setOpen(o => !o)}
          className='absolute top-2 left-2 z-50 px-3 py-1 rounded bg-gray-800 text-white text-xs shadow hover:bg-gray-700 focus:outline-none focus:ring'
      >
          {open ? "Hide" : "Show"}
      </button>

      <aside
          id="app-side-panel"
          className={`${open ? "flex" : "hidden"} flex-col w-[250px] flex-shrink-0 bg-white h-full border-8 border-gray-200 rounded-lg`}
      >
        <div className='p-4 border-b flex items-center justify-between'>
            <h2 className='text-sm font-semibold'>Menu</h2>
            <button
                type="button"
                onClick={() => setOpen(false)}
                className='text-md text-gray-500 hover:text-gray-700'
            >
                x
            </button>
        </div>
        <nav className='flex-1 overflow-y-auto p-3 space-y-6'>
            <section>
                <h3 className='text-xs font-semibold text-gray-500 uppercase mb-2'>Sections</h3>
                <ul className='space-y-1'>
                    <li className='text-sm px-2 py-1 rounded hover:bg-gray-200 cursor-pointer'>Conversation 1</li>
                </ul>
            </section>
            <section>
                <h3 className='text-xs font-medium text-gray-500 uppercase mb-2'>User</h3>
                <button className='w-full text-left text-sm px-2 py-1 rounded hover:bg-gray-200'>Profile</button>
                <button className='w-full text-left text-sm px-2 py-1 rounded hover:bg-gray-200'>Settings</button>
            </section>
        </nav>
        <div className='p-3 border-t'>
            <button className='w-full text-xs text-gray-600 hover:text-gray-900'>Log out</button>
        </div>
      </aside>
      </>
  );
}
export default SidePanel;