def set_axis(ax, **kwargs) -> None:
    """
    Function made to easely set a pyplot axis with the usual parameters.

        Args:
            ax: the axis on which apply the following elements
            
            kwargs: an indefinite number of parameters to set among which:

                xlabel, ylabel, title, xlim, ylim, legend, fontsize (for every label)
                labelsize (for the tick params), legend_fontsize, loc (position of the legend)
    """
        
    if 'labelsize' in kwargs:
        ax.tick_params(axis='both', which='major', labelsize=kwargs.get('labelsize', None))
    if 'xlabel' in kwargs:
        ax.set_xlabel(kwargs['xlabel'], fontsize=kwargs.get('fontsize', None))
    if 'ylabel' in kwargs:
        ax.set_ylabel(kwargs['ylabel'], fontsize=kwargs.get('fontsize', None))
    if 'title' in kwargs:
        ax.set_title(kwargs['title'], fontsize=kwargs.get('fontsize', None))
    if 'xlim' in kwargs:
        ax.set_xlim(kwargs['xlim'])
    if 'ylim' in kwargs:
        ax.set_ylim(kwargs['ylim'])
    if 'legend' in kwargs or 'legend_fontsize' in kwargs:
        ax.legend(fontsize=kwargs.get('legend_fontsize', None), loc=kwargs.get('loc', None))