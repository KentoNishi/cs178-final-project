import { getMyHarvardCourseInfo, getMyHarvardRequirements } from '../utils/scraper';
import Tooltip from '../components/Tooltip.svelte';

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
  };
  const interval = setInterval(callback, 100);
})();
