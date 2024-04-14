def progbar(cur, total, width, errorOcurred):
  frac = cur/total
  filled_progbar = round(frac * width)
  bar = "=" * filled_progbar + ">" + "." * (width - filled_progbar)
  colored_bar = "\x1b[31m" + bar if errorOcurred else bar
  print('\r', colored_bar, '[{:>7.2%}]'.format(frac), end='')