/*
 * makeETHNtupleReader.C
 *
 *  Created on: Nov 19, 2010
 *      Author: ale
 */

void makeETHZNtupleReader( const TString& treename, const TString& path) {
	std::cout << "Creating Reader for tree " << treename << " in file " << path << std::endl;
	TChain c(treename);
	c.Add(path);
	std::cout << "Nentries = " << c.GetEntries() << std::endl;
	if ( !c.GetTree() ) {
		std::cout << "The tree " << treename << " was not found in " << path << std::endl;
		return;
	}
	c.MakeClass("ETHZNtupleReader");

}
