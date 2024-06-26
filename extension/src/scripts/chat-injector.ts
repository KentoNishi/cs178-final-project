import { getMyHarvardCourseInfo, getMyHarvardRequirements } from '../utils/scraper';
import Tooltip from '../components/Tooltip.svelte';
import ChatPanel from '../components/ChatPanel.svelte';

(async () => {
  const [courses, requirements] = await Promise.all(
    [getMyHarvardCourseInfo(), getMyHarvardRequirements()]
  );
  const searchBar = document.querySelector('#IS_SCL_SearchTxt');
  const callback = () => {
    if (!searchBar) return;
    clearInterval(interval);
    const tooltipWrapper = document.createElement('div');
    tooltipWrapper.classList.add('tooltip');
    const tooltip = new Tooltip({
      target: tooltipWrapper,
    });
    searchBar?.after(tooltipWrapper);
    const chatPanel = new ChatPanel({
      target: document.body,
      props: {
      },
    });
    const googleMaterialFont = document.createElement('link');
    // <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" />
    googleMaterialFont.rel = 'stylesheet';
    googleMaterialFont.href = 'https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200';
    document.head.appendChild(googleMaterialFont);
  };
  const interval = setInterval(callback, 100);
})();
