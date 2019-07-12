#include "Analysis/VVAnalysis/interface/FakeRateSelector.h"
#include "Analysis/VVAnalysis/interface/SelectorBase.h"
//#include "Analysis/VVAnalysis/interface/ZSelector.h"

#include "Analysis/VVAnalysis/interface/WZSelector.h"
#include "Analysis/VVAnalysis/interface/WZSelectorBase.h"
#include "Analysis/VVAnalysis/interface/WZBackgroundSelector.h"
#include "Analysis/VVAnalysis/interface/ScaleFactor.h"
#include "Analysis/VVAnalysis/interface/disambiguateFinalStates.h"
#include "Analysis/VVAnalysis/interface/disambiguateFinalStatesZZ.h"
#include "Analysis/VVAnalysis/interface/SameSignLept.h"

namespace{
  namespace{
    FakeRateSelector pFakeRateSelector;
    WZSelectorBase pWZSelectorBase;
    SelectorBase pSelectorBase;
    //  ZSelector pZSelector;
    WZSelector pWZSelector;
    WZBackgroundSelector pWZBackgroundSelector;
    ScaleFactor pScaleFactor;
    disambiguateFinalStates pDisambiguator;
    disambiguateFinalStates pDisambiguatorZZ;
    SameSignLept pSameSignLept;
  }
}
