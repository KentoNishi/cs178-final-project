type Impure = () => void;

const performQuery: Impure = async () => {
  const searchBox = document.querySelector<HTMLInputElement>('#IS_SCL_SearchTxt');
  if (!searchBox) {
    return;
  }
  const searchParams = new URLSearchParams();
  searchParams.set("query", searchBox.value);

  const url = new URL("http://127.0.0.1:8000");
  url.search = searchParams.toString();

  const results = await fetch(url.href);

  console.log(results);
  return;
};

// Export a function that can be called from your Svelte component
export const performQueryWrapper = () => {
  performQuery(); // Call the async function
};